"""Slack and web tools for the `slack_ja` suite (same function names/semantics as upstream, Japanese descriptions)."""
from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from agentdojo.functions_runtime import Depends


class Message(BaseModel):
    sender: str = Field(..., title="メッセージの送信者")
    recipient: str = Field(..., title="メッセージの宛先（ユーザーまたはチャンネル）")
    body: str = Field(..., title="メッセージ本文")


class Slack(BaseModel):
    users: list[str] = Field(..., title="Slackのユーザー一覧")
    channels: list[str] = Field(..., title="Slackのチャンネル一覧")
    user_channels: dict[str, list[str]] = Field(..., title="各ユーザーが参加しているチャンネル")
    user_inbox: dict[str, list[Message]] = Field(..., title="各ユーザーの受信箱（DM）")
    channel_inbox: dict[str, list[Message]] = Field(..., title="各チャンネルのメッセージ")


class Web(BaseModel):
    web_content: dict[str, str]
    web_requests: list[str]


AnnotatedSlack = Annotated[Slack, Depends("slack")]
AnnotatedWeb = Annotated[Web, Depends("web")]


def get_channels(slack: AnnotatedSlack) -> list[str]:
    """Slackのチャンネル一覧を取得します。"""
    return slack.channels


def add_user_to_channel(slack: AnnotatedSlack, user: str, channel: str) -> None:
    """
    ユーザーを指定したチャンネルに追加します。

    :param user: チャンネルに追加するユーザー
    :param channel: ユーザーを追加するチャンネル
    """
    if user not in slack.users:
        raise ValueError(f"ユーザー {user} がユーザー一覧に見つかりません")
    if channel not in slack.channels:
        raise ValueError(f"チャンネル {channel} がチャンネル一覧に見つかりません")
    slack.user_channels[user].append(channel)


def read_channel_messages(slack: AnnotatedSlack, channel: str) -> list[Message]:
    """
    指定したチャンネルのメッセージを読み取ります。

    :param channel: メッセージを読み取るチャンネル
    """
    if channel not in slack.channels:
        raise ValueError("チャンネルが存在しません！")
    return slack.channel_inbox.get(channel, [])


def read_inbox(slack: AnnotatedSlack, user: str) -> list[Message]:
    """
    指定したユーザーの受信箱（DM）を読み取ります。

    :param user: 受信箱を読み取るユーザー
    """
    if user not in slack.users:
        raise ValueError(f"ユーザー {user} がユーザー一覧に見つかりません")
    return slack.user_inbox.get(user, [])


def send_direct_message(slack: AnnotatedSlack, recipient: str, body: str) -> None:
    """
    指定したユーザーにダイレクトメッセージ（DM）を送ります。

    :param recipient: メッセージの宛先ユーザー
    :param body: メッセージ本文
    """
    sender = "ボット"
    if recipient not in slack.users:
        raise ValueError(f"宛先 {recipient} がユーザー一覧に見つかりません")
    msg = Message(sender=sender, recipient=recipient, body=body)
    slack.user_inbox.setdefault(recipient, []).append(msg)


def send_channel_message(slack: AnnotatedSlack, channel: str, body: str) -> None:
    """
    指定したチャンネルにメッセージを投稿します。

    :param channel: メッセージを投稿するチャンネル
    :param body: メッセージ本文
    """
    sender = "ボット"
    if channel not in slack.channels:
        raise ValueError(f"チャンネル {channel} がチャンネル一覧に見つかりません")
    msg = Message(sender=sender, recipient=channel, body=body)
    slack.channel_inbox.setdefault(channel, []).append(msg)


def invite_user_to_slack(slack: AnnotatedSlack, user: str, user_email: str) -> None:
    """
    ユーザーをSlackワークスペースに招待します。

    :param user: 招待するユーザー
    :param user_email: 招待状を送るメールアドレス
    """
    if user in slack.users:
        raise ValueError(f"ユーザー {user} は既にユーザー一覧にいます")
    slack.users.append(user)
    slack.user_inbox[user] = []
    slack.user_channels[user] = []


def remove_user_from_slack(slack: AnnotatedSlack, user: str) -> None:
    """
    ユーザーをSlackワークスペースから削除します。

    :param user: 削除するユーザー
    """
    if user not in slack.users:
        raise ValueError(f"ユーザー {user} がユーザー一覧に見つかりません")
    slack.users.remove(user)
    del slack.user_inbox[user]
    del slack.user_channels[user]


def get_users_in_channel(slack: AnnotatedSlack, channel: str) -> list[str]:
    """
    指定したチャンネルに参加しているユーザーの一覧を取得します。

    :param channel: ユーザーを取得するチャンネル
    """
    if channel not in slack.channels:
        raise ValueError(f"チャンネル {channel} がチャンネル一覧に見つかりません")
    return [user for user, channels in slack.user_channels.items() if channel in channels]


def standardize_url(url: str) -> str:
    if url.startswith("https://"):
        url = url[8:]
    if url.startswith("http://"):
        url = url[7:]
    return url


def post_webpage(web: AnnotatedWeb, url: str, content: str) -> None:
    """
    指定したURLに、指定した内容のウェブページを公開します。

    :param url: ウェブページのURL
    :param content: ウェブページの内容
    """
    url = standardize_url(url)
    web.web_requests.append(url)
    web.web_content[url] = content


def get_webpage(web: AnnotatedWeb, url: str) -> str | None:
    """
    指定したURLのウェブページの内容を取得します。

    :param url: ウェブページのURL
    """
    url = standardize_url(url)
    web.web_requests.append(url)
    if url not in web.web_content:
        return "404 Not Found"
    return web.web_content.get(url)
