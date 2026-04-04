from fastapi import Request


async def rate_limit_guard(request: Request) -> None:  # pragma: no cover
    request.state.rate_limited = False
