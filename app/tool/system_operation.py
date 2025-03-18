"""系统操作工具，用于执行系统级文件和应用程序操作"""
import asyncio
import os
import shutil
import subprocess
import zipfile
import rarfile
import py7zr
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import win32gui
import win32con
from app.exceptions import ToolError
from app.logger import get_logger
from app.tool.base import BaseTool

logger = get_logger(__name__)

class SystemOperationTool(BaseTool):
    """系统操作工具，用于执行系统级文件和应用程序操作 💻"""

    name: str = "system_operation"
    description: str = "执行系统级操作，包括文件移动、复制、解压缩、打开应用程序等功能 🗂️"
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "要执行的操作类型",
                "enum": [
                    "copy_file", "move_file", "delete_file", "rename_file", 
                    "create_directory", "list_directory", "extract_archive", 
                    "compress_files", "open_file", "open_application"
                ],
            },
            "source_path": {
                "type": "string",
                "description": "源文件或目录的路径",
            },
            "target_path": {
                "type": "string",
                "description": "目标文件或目录的路径",
            },
            "file_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要操作的文件路径列表",
            },
            "archive_type": {
                "type": "string",
                "description": "压缩文件类型",
                "enum": ["zip", "rar", "7z"],
            },
            "application_path": {
                "type": "string",
                "description": "应用程序的路径",
            },
            "arguments": {
                "type": "string",
                "description": "应用程序的命令行参数",
            },
        },
        "required": ["action"],
    }

    async def execute(
        self,
        *,
        action: Literal[
            "copy_file", "move_file", "delete_file", "rename_file", 
            "create_directory", "list_directory", "extract_archive", 
            "compress_files", "open_file", "open_application"
        ],
        source_path: Optional[str] = None,
        target_path: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        archive_type: Optional[Literal["zip", "rar", "7z"]] = None,
        application_path: Optional[str] = None,
        arguments: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        执行系统操作 🔄
        
        Args:
            action: 要执行的操作类型
            source_path: 源文件或目录的路径
            target_path: 目标文件或目录的路径
            file_paths: 要操作的文件路径列表
            archive_type: 压缩文件类型
            application_path: 应用程序的路径
            arguments: 应用程序的命令行参数
            
        Returns:
            操作结果
        """
        try:
            # 根据操作类型执行相应功能
            if action == "copy_file":
                if not source_path or not target_path:
                    raise ToolError("复制文件需要提供源文件路径和目标路径 ❌")
                return await self._copy_file(source_path, target_path)
                
            elif action == "move_file":
                if not source_path or not target_path:
                    raise ToolError("移动文件需要提供源文件路径和目标路径 ❌")
                return await self._move_file(source_path, target_path)
                
            elif action == "delete_file":
                if not source_path:
                    raise ToolError("删除文件需要提供文件路径 ❌")
                return await self._delete_file(source_path)
                
            elif action == "rename_file":
                if not source_path or not target_path:
                    raise ToolError("重命名文件需要提供源文件路径和新文件名 ❌")
                return await self._rename_file(source_path, target_path)
                
            elif action == "create_directory":
                if not target_path:
                    raise ToolError("创建目录需要提供目录路径 ❌")
                return await self._create_directory(target_path)
                
            elif action == "list_directory":
                if not source_path:
                    raise ToolError("列出目录内容需要提供目录路径 ❌")
                return await self._list_directory(source_path)
                
            elif action == "extract_archive":
                if not source_path or not target_path:
                    raise ToolError("解压缩需要提供压缩文件路径和目标目录 ❌")
                return await self._extract_archive(source_path, target_path)
                
            elif action == "compress_files":
                if not file_paths or not target_path or not archive_type:
                    raise ToolError("压缩文件需要提供文件路径列表、目标压缩文件路径和压缩类型 ❌")
                return await self._compress_files(file_paths, target_path, archive_type)
                
            elif action == "open_file":
                if not source_path:
                    raise ToolError("打开文件需要提供文件路径 ❌")
                return await self._open_file(source_path)
                
            elif action == "open_application":
                if not application_path:
                    raise ToolError("打开应用程序需要提供应用程序路径 ❌")
                return await self._open_application(application_path, arguments)
                
            else:
                raise ToolError(f"不支持的操作: {action} ❌")
                
        except Exception as e:
            logger.error(f"系统操作失败: {str(e)} ❌")
            return {"success": False, "error": str(e)}

    async def _copy_file(self, source_path: str, target_path: str) -> Dict[str, Any]:
        """
        复制文件或目录 📋
        
        Args:
            source_path: 源文件或目录路径
            target_path: 目标路径
            
        Returns:
            复制结果
        """
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            raise ToolError(f"源文件或目录不存在: {source_path} ❌")
        
        # 确保目标目录存在
        if target.is_dir() or not target.parent.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if source.is_dir():
                # 复制目录
                if target.exists() and target.is_dir():
                    # 如果目标是目录，则复制到该目录下
                    target = target / source.name
                
                shutil.copytree(source, target)
                return {
                    "success": True,
                    "message": f"目录已成功复制: {source_path} -> {target_path} ✅",
                    "source": str(source),
                    "target": str(target)
                }
            else:
                # 复制文件
                if target.is_dir():
                    # 如果目标是目录，则复制到该目录下
                    target = target / source.name
                
                shutil.copy2(source, target)
                return {
                    "success": True,
                    "message": f"文件已成功复制: {source_path} -> {target_path} ✅",
                    "source": str(source),
                    "target": str(target)
                }
        except Exception as e:
            raise ToolError(f"复制失败: {str(e)} ❌")

    async def _move_file(self, source_path: str, target_path: str) -> Dict[str, Any]:
        """
        移动文件或目录 📦
        
        Args:
            source_path: 源文件或目录路径
            target_path: 目标路径
            
        Returns:
            移动结果
        """
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            raise ToolError(f"源文件或目录不存在: {source_path} ❌")
        
        # 确保目标目录存在
        if target.is_dir() or not target.parent.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if target.is_dir():
                # 如果目标是目录，则移动到该目录下
                target = target / source.name
            
            shutil.move(source, target)
            return {
                "success": True,
                "message": f"文件或目录已成功移动: {source_path} -> {target_path} ✅",
                "source": str(source),
                "target": str(target)
            }
        except Exception as e:
            raise ToolError(f"移动失败: {str(e)} ❌")

    async def _delete_file(self, source_path: str) -> Dict[str, Any]:
        """
        删除文件或目录 🗑️
        
        Args:
            source_path: 要删除的文件或目录路径
            
        Returns:
            删除结果
        """
        source = Path(source_path)
        
        if not source.exists():
            raise ToolError(f"文件或目录不存在: {source_path} ❌")
        
        try:
            if source.is_dir():
                shutil.rmtree(source)
                return {
                    "success": True,
                    "message": f"目录已成功删除: {source_path} ✅",
                    "deleted_path": str(source)
                }
            else:
                source.unlink()
                return {
                    "success": True,
                    "message": f"文件已成功删除: {source_path} ✅",
                    "deleted_path": str(source)
                }
        except Exception as e:
            raise ToolError(f"删除失败: {str(e)} ❌")

    async def _rename_file(self, source_path: str, target_path: str) -> Dict[str, Any]:
        """
        重命名文件或目录 📝
        
        Args:
            source_path: 源文件或目录路径
            target_path: 新名称路径
            
        Returns:
            重命名结果
        """
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            raise ToolError(f"源文件或目录不存在: {source_path} ❌")
        
        if target.exists():
            raise ToolError(f"目标路径已存在: {target_path} ❌")
        
        try:
            source.rename(target)
            return {
                "success": True,
                "message": f"文件或目录已成功重命名: {source_path} -> {target_path} ✅",
                "source": str(source),
                "target": str(target)
            }
        except Exception as e:
            raise ToolError(f"重命名失败: {str(e)} ❌")

    async def _create_directory(self, target_path: str) -> Dict[str, Any]:
        """
        创建目录 📁
        
        Args:
            target_path: 要创建的目录路径
            
        Returns:
            创建结果
        """
        target = Path(target_path)
        
        if target.exists():
            return {
                "success": True,
                "message": f"目录已存在: {target_path} ℹ️",
                "directory": str(target)
            }
        
        try:
            target.mkdir(parents=True, exist_ok=True)
            return {
                "success": True,
                "message": f"目录已成功创建: {target_path} ✅",
                "directory": str(target)
            }
        except Exception as e:
            raise ToolError(f"创建目录失败: {str(e)} ❌")

    async def _list_directory(self, source_path: str) -> Dict[str, Any]:
        """
        列出目录内容 📋
        
        Args:
            source_path: 要列出内容的目录路径
            
        Returns:
            目录内容列表
        """
        source = Path(source_path)
        
        if not source.exists():
            raise ToolError(f"目录不存在: {source_path} ❌")
        
        if not source.is_dir():
            raise ToolError(f"指定路径不是目录: {source_path} ❌")
        
        try:
            # 获取目录内容
            items = list(source.iterdir())
            
            # 分类为文件和目录
            files = [str(item) for item in items if item.is_file()]
            directories = [str(item) for item in items if item.is_dir()]
            
            return {
                "success": True,
                "message": f"已获取目录内容: {source_path} ✅",
                "directory": str(source),
                "files": files,
                "directories": directories,
                "total_items": len(items)
            }
        except Exception as e:
            raise ToolError(f"列出目录内容失败: {str(e)} ❌")

    async def _extract_archive(self, source_path: str, target_path: str) -> Dict[str, Any]:
        """
        解压缩文件 📦
        
        Args:
            source_path: 压缩文件路径
            target_path: 解压目标目录
            
        Returns:
            解压结果
        """
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            raise ToolError(f"压缩文件不存在: {source_path} ❌")
        
        # 确保目标目录存在
        target.mkdir(parents=True, exist_ok=True)
        
        try:
            file_extension = source.suffix.lower()
            
            if file_extension == '.zip':
                # 解压ZIP文件
                with zipfile.ZipFile(source, 'r') as zip_ref:
                    zip_ref.extractall(target)
                    extracted_files = zip_ref.namelist()
            
            elif file_extension == '.rar':
                # 解压RAR文件
                with rarfile.RarFile(source, 'r') as rar_ref:
                    rar_ref.extractall(target)
                    extracted_files = rar_ref.namelist()
            
            elif file_extension == '.7z':
                # 解压7Z文件
                with py7zr.SevenZipFile(source, 'r') as sz_ref:
                    sz_ref.extractall(target)
                    extracted_files = [f.filename for f in sz_ref.list()]
            
            else:
                raise ToolError(f"不支持的压缩文件格式: {file_extension} ❌")
            
            return {
                "success": True,
                "message": f"文件已成功解压: {source_path} -> {target_path} ✅",
                "source": str(source),
                "target": str(target),
                "extracted_files_count": len(extracted_files)
            }
        except Exception as e:
            raise ToolError(f"解压失败: {str(e)} ❌")

    async def _compress_files(self, file_paths: List[str], target_path: str, archive_type: str) -> Dict[str, Any]:
        """
        压缩文件 📦
        
        Args:
            file_paths: 要压缩的文件路径列表
            target_path: 目标压缩文件路径
            archive_type: 压缩文件类型
            
        Returns:
            压缩结果
        """
        target = Path(target_path)
        
        # 检查所有源文件是否存在
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                raise ToolError(f"源文件或目录不存在: {file_path} ❌")
        
        # 确保目标目录存在
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # 确保文件扩展名与压缩类型匹配
        if not target_path.lower().endswith(f'.{archive_type}'):
            target = Path(f"{target_path}.{archive_type}")
        
        try:
            if archive_type == 'zip':
                # 创建ZIP文件
                with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for file_path in file_paths:
                        path = Path(file_path)
                        if path.is_dir():
                            # 如果是目录，添加目录下所有文件
                            for root, _, files in os.walk(path):
                                for file in files:
                                    file_full_path = os.path.join(root, file)
                                    zip_ref.write(
                                        file_full_path, 
                                        os.path.relpath(file_full_path, os.path.dirname(path))
                                    )
                        else:
                            # 如果是文件，直接添加
                            zip_ref.write(path, path.name)
            
            elif archive_type == 'rar':
                # 创建RAR文件 - 注意：Python的rarfile模块不支持创建RAR文件，这里使用外部命令
                raise ToolError("Python的rarfile模块不支持创建RAR文件，请使用其他压缩格式 ❌")
            
            elif archive_type == '7z':
                # 创建7Z文件
                with py7zr.SevenZipFile(target, 'w') as sz_ref:
                    for file_path in file_paths:
                        path = Path(file_path)
                        if path.is_dir():
                            # 如果是目录，添加整个目录
                            sz_ref.writeall(path, arcname=path.name)
                        else:
                            # 如果是文件，直接添加
                            sz_ref.write(path, path.name)
            
            else:
                raise ToolError(f"不支持的压缩文件格式: {archive_type} ❌")
            
            return {
                "success": True,
                "message": f"文件已成功压缩: {file_paths} -> {target} ✅",
                "source_files": file_paths,
                "target": str(target)
            }
        except Exception as e:
            raise ToolError(f"压缩失败: {str(e)} ❌")

    async def _open_file(self, source_path: str) -> Dict[str, Any]:
        """
        打开文件 📄
        
        Args:
            source_path: 要打开的文件路径
            
        Returns:
            打开结果
        """
        source = Path(source_path)
        
        if not source.exists():
            raise ToolError(f"文件不存在: {source_path} ❌")
        
        if not source.is_file():
            raise ToolError(f"指定路径不是文件: {source_path} ❌")
        
        try:
            # 使用系统默认程序打开文件
            os.startfile(source)
            
            return {
                "success": True,
                "message": f"文件已成功打开: {source_path} ✅",
                "file": str(source)
            }
        except Exception as e:
            raise ToolError(f"打开文件失败: {str(e)} ❌")

    async def _open_application(self, application_path: str, arguments: Optional[str] = None) -> Dict[str, Any]:
        """
        打开应用程序 🖥️
        
        Args:
            application_path: 应用程序路径
            arguments: 命令行参数
            
        Returns:
            打开结果
        """
        app_path = Path(application_path)
        
        if not app_path.exists() and not shutil.which(application_path):
            raise ToolError(f"应用程序不存在: {application_path} ❌")
        
        try:
            # 构建命令
            cmd = f'"{application_path}"'
            if arguments:
                cmd += f' {arguments}'
            
            # 启动应用程序
            subprocess.Popen(cmd, shell=True)
            
            return {
                "success": True,
                "message": f"应用程序已成功启动: {application_path} {arguments or ''} ✅",
                "application": application_path,
                "arguments": arguments
            }
        except Exception as e:
            raise ToolError(f"启动应用程序失败: {str(e)} ❌")