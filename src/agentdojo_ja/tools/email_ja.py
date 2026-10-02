"""Email tools (Japanese descriptions/messages). Data models are upstream's; contacts are listed explicitly in the
environment YAML so Japanese names (田中 太郎) can be searched (upstream derives names like "Tanaka Taro" from addresses)."""
from __future__ import annotations

from typing import Annotated

from agentdojo.default_suites.v1.tools.email_client import EmailContact, Inbox
from agentdojo.default_suites.v1.tools.types import CalendarEvent, CloudDriveFileID, Email
from agentdojo.functions_runtime import Depends

__all__ = [
    "EmailContact",
    "Inbox",
    "delete_email",
    "get_draft_emails",
    "get_received_emails",
    "get_sent_emails",
    "get_unread_emails",
    "search_contacts_by_email",
    "search_contacts_by_name",
    "search_emails",
    "send_email",
]


def get_unread_emails(inbox: Annotated[Inbox, Depends("inbox")]) -> list[Email]:
    """受信箱の未読メールを全て返します。各メールには送信者・件名・本文があります。この関数を呼ぶと、メールは既読になります。"""
    return inbox.get_unread()


def send_email(
    inbox: Annotated[Inbox, Depends("inbox")],
    recipients: list[str],
    subject: str,
    body: str,
    attachments: list[dict] | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
) -> Email:
    """
    指定した宛先に、指定した本文のメールを送信します。メールの詳細を返します。

    :param recipients: 宛先のメールアドレスのリスト
    :param subject: メールの件名
    :param body: メールの本文
    :param attachments: 添付のリスト。`null`の場合は添付なし。
    添付の"type"が"file"の場合は、クラウドドライブ上のファイルIDを持つ"file_id"フィールドが必要です。
    "type"が"event"の場合は、"event_details"フィールドにカレンダーの予定を指定します。
    予定には`title`、`description`、`start_time`（ISO形式）、`end_time`（ISO形式）、`location`、participants（メールアドレスのリスト）があります。
    :param cc: CCに含めるメールアドレスのリスト。`null`の場合はなし。
    :param bcc: BCCに含めるメールアドレスのリスト。`null`の場合はなし。
    """
    parsed = None
    if attachments is not None:
        parsed = []
        for attachment in attachments:
            if not isinstance(attachment, dict):
                raise ValueError("添付は辞書で指定してください。")
            if "type" not in attachment:
                raise ValueError("添付には'type'フィールドが必要です。")
            if attachment["type"] == "file" or "file_id" in attachment:
                if "file_id" not in attachment:
                    raise ValueError("'file'タイプの添付には'file_id'フィールドが必要です。")
                parsed.append(CloudDriveFileID(attachment["file_id"]))
            else:
                if "event_details" not in attachment:
                    raise ValueError("'event'タイプの添付には'event_details'フィールドが必要です。")
                parsed.append(CalendarEvent(**attachment["event_details"]))
    return inbox.send_email(recipients, subject, body, parsed, cc, bcc)


def search_emails(inbox: Annotated[Inbox, Depends("inbox")], query: str, sender: str | None = None) -> list[Email]:
    """
    受信箱から、件名または本文に検索語を含むメールを探します。`sender`を指定した場合は、その送信者のメールだけを探します。

    :param query: メールの件名または本文から探す検索語。空の場合は全てのメールを返します。
    :param sender: 送信者のメールアドレス。`null`の場合は全てのメールから探します。アドレスが分からない場合は`search_contacts_by_name`を使ってください。
    """
    matches = inbox.search_emails(query, sender)
    if len(matches) == 0:
        raise ValueError("メールが見つかりません。別の検索語で試してください。")
    return matches


def delete_email(inbox: Annotated[Inbox, Depends("inbox")], email_id: str) -> str:
    """
    指定したIDのメールを受信箱から削除します。

    :param email_id: 削除するメールのID
    """
    inbox.delete_email(email_id)
    return f"ID {email_id} のメールを削除しました。"


def get_sent_emails(inbox: Annotated[Inbox, Depends("inbox")]) -> list[Email]:
    """送信済みメールを全て返します。各メールには宛先・件名・本文があります。"""
    return inbox.sent


def get_received_emails(inbox: Annotated[Inbox, Depends("inbox")]) -> list[Email]:
    """受信済みメールを全て返します。各メールには送信者・件名・本文があります。"""
    return inbox.received


def get_draft_emails(inbox: Annotated[Inbox, Depends("inbox")]) -> list[Email]:
    """下書きメールを全て返します。各メールには宛先・件名・本文があります。"""
    return inbox.drafts


def search_contacts_by_name(inbox: Annotated[Inbox, Depends("inbox")], query: str) -> list[EmailContact]:
    """
    受信箱の連絡先リストから、名前で連絡先を探します。名前が一致する連絡先のリストを返します。

    :param query: 探す連絡先の名前
    """
    return inbox.find_contacts_by_name(query)


def search_contacts_by_email(inbox: Annotated[Inbox, Depends("inbox")], query: str) -> list[EmailContact]:
    """
    受信箱の連絡先リストから、メールアドレスで連絡先を探します。アドレスが一致する連絡先のリストを返します。

    :param query: 探す連絡先のメールアドレス
    """
    return inbox.find_contacts_by_email(query)
