#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import uvicorn
from fastapi import Body, FastAPI
from pydantic import BaseModel


class Msg(BaseModel):
    is_self: bool
    is_group: bool
    id: int
    type: int
    ts: int
    roomid: str
    content: str
    sender: str
    sign: str
    thumb: str
    extra: str
    xml: str


def msg_cb(msg: Msg = Body(description="微信消息")):
    """示例回调方法，简单打印消息"""
    print(f"收到消息：{msg}")
    return {"status": 0, "message": "成功"}


if __name__ == "__main__":
    app = FastAPI()
    app.add_api_route("/callback", msg_cb, methods=["POST"])
    uvicorn.run(app, host="0.0.0.0", port=8000)