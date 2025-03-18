import os
import base64
from typing import Dict, List, Literal, Optional, Any
from pathlib import Path

from app.exceptions import ToolError
from app.tool.base import BaseTool
from app.logger import get_logger
from app.llm import LLM
from app.config import Config  # 导入Config类

logger = get_logger(__name__)

class MediaProcessTool(BaseTool):
    """媒体处理工具，用于处理图片和文档，支持多模型协作处理 🖼️📄"""

    name: str = "media_process"
    description: str = """
    处理上传的图片和文档文件，支持以下功能：
    1. 图片分析：使用视觉大模型分析图片内容
    2. 文档处理：使用思考大模型分析和处理文档内容
    3. 结果保存：将处理结果保存到文件
    
    当用户上传图片时，会先使用视觉大模型分析，再用思考大模型美化结果；
    当用户上传文档时，会直接使用思考大模型进行分析处理。
    如果用户要求保存结果，会使用执行大模型完成保存操作。
    """
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "要执行的操作类型",
                "enum": ["process_image", "process_document", "save_result"],
            },
            "file_path": {
                "type": "string",
                "description": "要处理的文件路径",
            },
            "prompt": {
                "type": "string",
                "description": "用户提供的处理提示",
            },
            "result": {
                "type": "string",
                "description": "处理结果，用于保存操作",
            },
            "save_path": {
                "type": "string",
                "description": "保存结果的文件路径",
            },
        },
        "required": ["action"],
    }

    def __init__(self):
        super().__init__()
        
    async def execute(
        self,
        *,
        action: Literal["process_image", "process_document", "save_result"],
        file_path: Optional[str] = None,
        prompt: Optional[str] = None,
        result: Optional[str] = None,
        save_path: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        执行媒体处理操作 🔄
        
        Args:
            action: 要执行的操作类型
            file_path: 要处理的文件路径
            prompt: 用户提供的处理提示
            result: 处理结果，用于保存操作
            save_path: 保存结果的文件路径
            
        Returns:
            操作结果
        """
        try:
            if action == "process_image":
                if not file_path or not prompt:
                    raise ToolError("处理图片需要提供图片路径和处理提示 ❌")
                return await self._process_image(file_path, prompt)
                
            elif action == "process_document":
                if not file_path or not prompt:
                    raise ToolError("处理文档需要提供文档路径和处理提示 ❌")
                return await self._process_document(file_path, prompt)
                
            elif action == "save_result":
                if not result or not save_path:
                    raise ToolError("保存结果需要提供处理结果和保存路径 ❌")
                return await self._save_result(result, save_path)
                
            else:
                raise ToolError(f"不支持的操作类型: {action} ❌")
                
        except Exception as e:
            logger.error(f"媒体处理工具执行失败: {str(e)}")
            raise ToolError(f"媒体处理工具执行失败: {str(e)} ❌")
    
    async def _process_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        处理图片：先用视觉大模型分析，再用思考大模型美化
        
        Args:
            image_path: 图片路径
            prompt: 用户提示
            
        Returns:
            处理结果
        """
        logger.info(f"开始处理图片: {image_path}")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise ToolError(f"图片文件不存在: {image_path} ❌")
        
        # 检查是否为图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if not any(image_path.lower().endswith(ext) for ext in image_extensions):
            raise ToolError(f"文件不是支持的图片格式: {image_path} ❌")
        
        try:
            # 读取图片文件
            with open(image_path, 'rb') as f:
                img_data = f.read()
            
            # 1. 使用视觉大模型分析图片
            logger.info("正在使用视觉大模型分析图片...")
            vision_result = await self._call_vision_model(prompt, img_data)
            
            # 2. 将分析结果传递给思考大模型进行美化处理
            logger.info("正在使用思考大模型美化分析结果...")
            thinking_prompt = f"以下是视觉模型对图片的分析结果，请对其进行美化和深入处理:\n\n{vision_result}\n\n用户原始提示: {prompt}"
            thinking_result = await self._call_thinking_model(thinking_prompt)
            
            # 检查是否需要保存
            save_request = self._check_save_request(prompt)
            
            # 3. 如果需要保存，使用执行大模型保存结果
            if save_request:
                logger.info("检测到保存请求，正在保存处理结果...")
                
                # 生成保存文件名
                base_name = os.path.basename(image_path)
                file_name, _ = os.path.splitext(base_name)
                save_path = os.path.join(os.path.dirname(image_path), f"{file_name}_分析结果.txt")
                
                # 保存结果
                save_result = await self._save_result(thinking_result, save_path)
                
                return {
                    "success": True,
                    "message": "图片处理完成并已保存结果 ✅",
                    "vision_result": vision_result,
                    "thinking_result": thinking_result,
                    "save_result": save_result.get("message", ""),
                    "save_path": save_path
                }
            else:
                return {
                    "success": True,
                    "message": "图片处理完成 ✅",
                    "vision_result": vision_result,
                    "thinking_result": thinking_result
                }
                
        except Exception as e:
            logger.error(f"处理图片时出错: {str(e)}")
            raise ToolError(f"处理图片时出错: {str(e)} ❌")
    
    async def _process_document(self, doc_path: str, prompt: str) -> Dict[str, Any]:
        """
        处理文档：使用思考大模型分析和处理
        
        Args:
            doc_path: 文档路径
            prompt: 用户提示
            
        Returns:
            处理结果
        """
        logger.info(f"开始处理文档: {doc_path}")
        
        # 检查文件是否存在
        if not os.path.exists(doc_path):
            raise ToolError(f"文档文件不存在: {doc_path} ❌")
        
        try:
            # 读取文档内容
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(doc_path, 'r', encoding='gbk') as f:
                        content = f.read()
                except:
                    raise ToolError(f"无法读取文档内容，可能是二进制文件: {doc_path} ❌")
            
            # 使用思考大模型分析文档
            logger.info("正在使用思考大模型分析文档...")
            thinking_prompt = f"以下是文档内容，请根据用户提示进行分析和处理:\n\n文档内容:\n{content}\n\n用户提示: {prompt}"
            thinking_result = await self._call_thinking_model(thinking_prompt)
            
            # 检查是否需要保存
            save_request = self._check_save_request(prompt)
            
            # 如果需要保存，保存结果
            if save_request:
                logger.info("检测到保存请求，正在保存处理结果...")
                
                # 生成保存文件名
                base_name = os.path.basename(doc_path)
                file_name, ext = os.path.splitext(base_name)
                save_path = os.path.join(os.path.dirname(doc_path), f"{file_name}_处理结果{ext}")
                
                # 保存结果
                save_result = await self._save_result(thinking_result, save_path)
                
                return {
                    "success": True,
                    "message": "文档处理完成并已保存结果 ✅",
                    "thinking_result": thinking_result,
                    "save_result": save_result.get("message", ""),
                    "save_path": save_path
                }
            else:
                return {
                    "success": True,
                    "message": "文档处理完成 ✅",
                    "thinking_result": thinking_result
                }
                
        except Exception as e:
            logger.error(f"处理文档时出错: {str(e)}")
            raise ToolError(f"处理文档时出错: {str(e)} ❌")
    
    async def _save_result(self, content: str, save_path: str) -> Dict[str, Any]:
        """
        保存处理结果到文件
        
        Args:
            content: 要保存的内容
            save_path: 保存路径
            
        Returns:
            保存结果
        """
        logger.info(f"正在保存结果到: {save_path}")
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            
            # 保存文件
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"结果已成功保存到: {save_path} ✅",
                "save_path": save_path
            }
        except Exception as e:
            logger.error(f"保存结果时出错: {str(e)}")
            raise ToolError(f"保存结果时出错: {str(e)} ❌")
    
    async def _call_vision_model(self, prompt: str, img_data: bytes) -> str:
        """调用视觉大模型"""
        try:
            # 从配置中获取视觉模型信息
            vision_config = self.config._config.get("llm", {}).get("vision", {})
            if not vision_config:
                raise ToolError("未找到视觉模型配置 ❌")
            
            # 创建视觉LLM实例
            vision_llm = LLM("vision", vision_config)
            
            # 将图片转换为base64
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # 构建包含图片的消息
            messages = [
                {"role": "system", "content": "你是一个专业的图像分析助手，请详细分析图片内容并提供准确的描述。"},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]}
            ]
            
            # 调用视觉模型
            response = vision_llm.chat_completion(messages=messages)
            
            return response.get("choices", [{}])[0].get("message", {}).get("content", "无法获取视觉模型分析结果")
            
        except Exception as e:
            logger.error(f"视觉模型调用失败: {str(e)}")
            raise ToolError(f"视觉模型调用失败: {str(e)} ❌")
    
    async def _call_thinking_model(self, prompt: str) -> str:
        """调用思考大模型"""
        try:
            # 从配置中获取思考模型信息
            thinking_config = self.config._config.get("llm", {}).get("thinking", {})
            if not thinking_config:
                raise ToolError("未找到思考模型配置 ❌")
            
            # 创建思考LLM实例
            thinking_llm = LLM("thinking", thinking_config)
            
            # 构建消息
            messages = [
                {"role": "system", "content": "你是一个专业的内容分析和处理助手，请根据用户提示进行深入分析和处理。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用思考模型
            response = thinking_llm.chat_completion(messages=messages)
            
            return response.get("choices", [{}])[0].get("message", {}).get("content", "无法获取思考模型处理结果")
            
        except Exception as e:
            logger.error(f"思考模型调用失败: {str(e)}")
            raise ToolError(f"思考模型调用失败: {str(e)} ❌")
    
    async def _call_execution_model(self, prompt: str) -> str:
        """调用执行大模型"""
        try:
            # 从配置中获取执行模型信息
            execution_config = self.config._config.get("llm", {}).get("execution", {})
            if not execution_config:
                raise ToolError("未找到执行模型配置 ❌")
            
            # 创建执行LLM实例
            execution_llm = LLM("execution", execution_config)
            
            # 构建消息
            messages = [
                {"role": "system", "content": "你是一个专业的任务执行助手，请根据用户提示执行相应的操作。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用执行模型
            response = execution_llm.chat_completion(messages=messages)
            
            return response.get("choices", [{}])[0].get("message", {}).get("content", "无法获取执行模型处理结果")
            
        except Exception as e:
            logger.error(f"执行模型调用失败: {str(e)}")
            raise ToolError(f"执行模型调用失败: {str(e)} ❌")
    
    def _check_save_request(self, prompt: str) -> bool:
        """检查用户是否要求保存处理结果"""
        save_keywords = ["保存", "存储", "另存为", "保存下来", "保存到", "存到", "导出"]
        return any(keyword in prompt for keyword in save_keywords)