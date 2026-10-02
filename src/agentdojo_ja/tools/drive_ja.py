"""Cloud-drive tools (Japanese descriptions/messages). Data models are upstream's.

Differences from upstream: the `delete_file` description says the file is deleted by ID (upstream's docstring says
"by its filename" although the argument is `file_id`).
"""

from typing import Annotated

from agentdojo.default_suites.v1.tools.cloud_drive_client import CloudDrive
from agentdojo.default_suites.v1.tools.types import CloudDriveFile, CloudDriveFileID, SharingPermission
from agentdojo.functions_runtime import Depends

__all__ = [
    "CloudDrive",
    "append_to_file",
    "create_file",
    "delete_file",
    "get_file_by_id",
    "list_files",
    "search_files",
    "search_files_by_filename",
    "share_file",
]


def search_files_by_filename(
    cloud_drive: Annotated[CloudDrive, Depends("cloud_drive")], filename: str
) -> list[CloudDriveFile]:
    """
    ファイル名で、クラウドドライブからファイルを探します。ファイルのリストを返します。
    各ファイルには、ファイルID、内容、ファイル名などが含まれます。

    :param filename: 探すファイルの名前（一部でも可）
    """
    return cloud_drive.search_files_by_filename(filename)


def create_file(cloud_drive: Annotated[CloudDrive, Depends("cloud_drive")], filename: str, content: str) -> CloudDriveFile:
    """
    クラウドドライブに、新しいファイルを作成します。

    :param filename: 作成するファイルの名前
    :param content: 作成するファイルの内容
    """
    return cloud_drive.create_file(filename, content)


def delete_file(cloud_drive: Annotated[CloudDrive, Depends("cloud_drive")], file_id: str) -> CloudDriveFile:
    """
    クラウドドライブから、IDを指定してファイルを削除します。削除したファイルを返します。

    :param file_id: 削除するファイルのID
    """
    return cloud_drive.delete_file(CloudDriveFileID(file_id))


def get_file_by_id(cloud_drive: Annotated[CloudDrive, Depends("cloud_drive")], file_id: str) -> CloudDriveFile:
    """
    クラウドドライブから、IDを指定してファイルを取得します。

    :param file_id: 取得するファイルのID
    """
    return cloud_drive.get_file_by_id(file_id)


def list_files(cloud_drive: Annotated[CloudDrive, Depends("cloud_drive")]) -> list[CloudDriveFile]:
    """クラウドドライブにある、全てのファイルを取得します。"""
    return list(cloud_drive.files.values())


def share_file(
    cloud_drive: Annotated[CloudDrive, Depends("cloud_drive")],
    file_id: str,
    email: str,
    permission: SharingPermission,
) -> CloudDriveFile:
    """
    ファイルを、指定したユーザーと共有します。

    :param file_id: 共有するファイルのID
    :param email: ファイルを共有するユーザーのメールアドレス
    :param permission: ユーザーに付与する権限（"r"は読み取り、"rw"は読み書き）
    """
    file = cloud_drive.get_file_by_id(CloudDriveFileID(file_id))
    file.shared_with[email] = permission
    return file


def append_to_file(
    cloud_drive: Annotated[CloudDrive, Depends("cloud_drive")], file_id: str, content: str
) -> CloudDriveFile:
    """
    クラウドドライブ上のファイルの末尾に、内容を追記します。

    :param file_id: 追記するファイルのID
    :param content: ファイルに追記する内容
    """
    return cloud_drive.append_to_file(CloudDriveFileID(file_id), content)


def search_files(cloud_drive: Annotated[CloudDrive, Depends("cloud_drive")], query: str) -> list[CloudDriveFile]:
    """
    クラウドドライブのファイルを、内容で検索します。

    :param query: ファイルの中から探す文字列
    """
    matches = cloud_drive.search_files(query)
    if len(matches) == 0:
        raise ValueError(f"検索語（'{query}'）に一致するファイルが見つかりません。別の検索語で試してください。")
    return matches
