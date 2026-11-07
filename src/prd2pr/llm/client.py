"""LiteLLM wrapper for summaries and embeddings."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from typing import Any

import litellm

logger = logging.getLogger(__name__)

# Quiet litellm noise by default
litellm.suppress_debug_info = True


class LlmClient:
    def __init__(
        self,
        summary_model: str,
        embedding_model: str,
        embedding_dim: int,
        concurrency: int = 8,
    ) -> None:
        self.summary_model = summary_model
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim
        self.concurrency = concurrency
        self.total_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0

    async def _retry(self, coro_factory: Any, retries: int = 3) -> Any:
        delay = 0.5
        last_exc: Exception | None = None
        for attempt in range(retries):
            try:
                return await coro_factory()
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning("LLM call failed (attempt %s): %s", attempt + 1, exc)
                await asyncio.sleep(delay)
                delay *= 2
        assert last_exc is not None
        raise last_exc

    async def summarize(self, header: str, code: str) -> str:
        prompt = (
            "In 1-2 plain English sentences, summarize what this code does "
            "(business meaning, not syntax).\n\n"
            f"{header}\n\n```\n{code[:6000]}\n```"
        )

        async def _call() -> Any:
            return await litellm.acompletion(
                model=self.summary_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=120,
            )

        resp = await self._retry(_call)
        self.call_count += 1
        usage = getattr(resp, "usage", None)
        if usage:
            self.total_tokens += int(getattr(usage, "total_tokens", 0) or 0)
        try:
            self.total_cost += float(litellm.completion_cost(completion_response=resp) or 0)
        except Exception:  # noqa: BLE001
            pass
        content = resp.choices[0].message.content or ""
        return content.strip()

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        async def _call() -> Any:
            return await litellm.aembedding(
                model=self.embedding_model,
                input=list(texts),
            )

        resp = await self._retry(_call)
        self.call_count += 1
        usage = getattr(resp, "usage", None)
        if usage:
            self.total_tokens += int(getattr(usage, "total_tokens", 0) or 0)
        data = resp.data
        # Sort by index if present
        sorted_data = sorted(data, key=lambda d: getattr(d, "index", 0))
        vectors: list[list[float]] = []
        for d in sorted_data:
            emb = d["embedding"] if isinstance(d, dict) else d.embedding
            vectors.append(list(emb))
        return vectors

    async def summarize_many(
        self, items: Sequence[tuple[str, str, str]]
    ) -> dict[str, str]:
        """items: (chunk_id, header, code) → map chunk_id → summary."""
        sem = asyncio.Semaphore(self.concurrency)
        results: dict[str, str] = {}

        async def one(cid: str, header: str, code: str) -> None:
            async with sem:
                try:
                    results[cid] = await self.summarize(header, code)
                except Exception as exc:  # noqa: BLE001
                    logger.error("summary failed for %s: %s", cid, exc)

        await asyncio.gather(*(one(cid, h, c) for cid, h, c in items))
        return results

    async def embed_many(self, texts: Sequence[str], batch_size: int = 32) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            out.extend(await self.embed(batch))
        return out
