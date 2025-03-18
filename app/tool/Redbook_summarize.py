import asyncio
import os
import time
import re
from typing import List, Dict, Optional, Any, Union
from pathlib import Path

from app.tool.base import BaseTool, ToolError, ToolResult

# 尝试导入 XHS-Spider 库
try:
    import xhs_spider
    from xhs_spider.spider import XHSSpider
    XHS_SPIDER_AVAILABLE = True
except ImportError:
    XHS_SPIDER_AVAILABLE = False

# 尝试导入 docx 库用于创建Word文档
try:
    import docx
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# 尝试导入requests库用于网络请求
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class RedbookSummarize(BaseTool):
    """小红书内容搜索与总结工具"""

    name: str = "redbook_summarize"
    description: str = """
    使用XHS-Spider库搜索小红书内容，抓取多篇文章并进行总结。
    可以搜索特定关键词，抓取多篇笔记内容，并生成总结报告保存到指定路径。
    当您需要了解小红书上关于某个话题的内容趋势和观点时，请使用此工具。
    """
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(required) 要在小红书上搜索的关键词",
            },
            "article_count": {
                "type": "integer",
                "description": "要抓取的文章数量，默认为5篇",
                "default": 5,
            },
            "save_path": {
                "type": "string",
                "description": "总结报告保存路径，默认为桌面",
                "default": os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
            },
            "include_images": {
                "type": "boolean",
                "description": "是否包含图片，默认为True",
                "default": True,
            },
        },
        "required": ["query"],
    }

    async def execute(
        self,
        query: str,
        article_count: int = 5,
        save_path: str = None,
        include_images: bool = True,
        **kwargs
    ) -> Union[str, Dict[str, Any]]:
        """
        执行小红书内容搜索与总结。

        Args:
            query: 要搜索的关键词
            article_count: 要抓取的文章数量
            save_path: 总结报告保存路径
            include_images: 是否包含图片

        Returns:
            操作结果，包含总结内容和保存路径
        """
        # 设置默认保存路径
        if save_path is None:
            save_path = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
        
        # 检查依赖
        if not XHS_SPIDER_AVAILABLE:
            raise ToolError("无法使用XHS-Spider库，请安装: pip install xhs-spider")
            
        if not DOCX_AVAILABLE:
            raise ToolError("无法创建Word文档，请安装必要的库: pip install python-docx")
            
        if include_images and not REQUESTS_AVAILABLE:
            raise ToolError("无法下载图片，请安装必要的库: pip install requests")

        # 在线程池中运行操作以防止阻塞
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: self._execute_sync(query, article_count, save_path, include_images)
        )
        
        return result

    def _execute_sync(
        self,
        query: str,
        article_count: int,
        save_path: str,
        include_images: bool,
    ) -> Dict[str, Any]:
        """同步执行小红书内容搜索与总结"""
        try:
            # 使用XHS-Spider库抓取内容
            articles = self._scrape_with_spider(query, article_count, include_images)
            
            # 生成总结
            summary = self._generate_summary(query, articles)
            
            # 保存总结到文件
            file_path = self._save_summary(summary, save_path, query, articles)
            
            return {
                "query": query,
                "article_count": len(articles),
                "summary": summary,
                "file_path": file_path,
            }
        except Exception as e:
            raise ToolError(f"执行小红书内容搜索与总结时出错: {str(e)}")

    def _scrape_with_spider(self, query: str, article_count: int, include_images: bool) -> List[Dict[str, Any]]:
        """使用XHS-Spider库抓取小红书内容"""
        try:
            # 初始化爬虫
            spider = XHSSpider()
            
            # 搜索笔记
            print(f"正在使用XHS-Spider搜索关键词: {query}")
            search_results = spider.search_notes(query, limit=article_count*2)  # 获取更多结果以防有些无法获取详情
            
            if not search_results:
                raise ToolError(f"未找到关于'{query}'的搜索结果")
            
            articles = []
            for i, note in enumerate(search_results):
                if len(articles) >= article_count:
                    break
                    
                try:
                    # 获取笔记详情
                    note_id = note.get('id') or note.get('note_id')
                    if not note_id:
                        continue
                        
                    print(f"正在抓取笔记 {len(articles)+1}/{article_count}, ID: {note_id}")
                    note_detail = spider.get_note_detail(note_id)
                    
                    if not note_detail:
                        print(f"无法获取笔记详情，ID: {note_id}")
                        continue
                    
                    # 提取笔记信息
                    title = note_detail.get('title') or note.get('title') or f"笔记 {len(articles)+1}"
                    author = note_detail.get('user', {}).get('nickname') or "未知作者"
                    content = note_detail.get('desc') or note_detail.get('content') or "无内容"
                    likes = str(note_detail.get('likes') or note_detail.get('like_count') or "未知")
                    url = f"https://www.xiaohongshu.com/discovery/item/{note_id}"
                    
                    # 保存图片
                    image_paths = []
                    if include_images:
                        images = note_detail.get('images') or note_detail.get('image_list') or []
                        
                        for j, img_url in enumerate(images[:3]):  # 只保存前3张图片
                            try:
                                img_path = os.path.join(os.environ.get('TEMP', ''), f"xhs_{note_id}_{j}.jpg")
                                if self._download_image(img_url, img_path):
                                    image_paths.append(img_path)
                            except Exception as e:
                                print(f"下载图片时出错: {str(e)}")
                    
                    articles.append({
                        "title": title,
                        "author": author,
                        "content": content,
                        "likes": likes,
                        "note_id": note_id,
                        "url": url,
                        "images": image_paths,
                        "created_time": note_detail.get('time') or note_detail.get('created_time') or "",
                        "topics": note_detail.get('topics') or []
                    })
                    
                except Exception as e:
                    print(f"抓取笔记时出错: {str(e)}")
                    continue
            
            if not articles:
                raise ToolError(f"未能成功抓取关于'{query}'的任何笔记")
                
            return articles
            
        except Exception as e:
            raise ToolError(f"使用XHS-Spider抓取内容时出错: {str(e)}")

    def _download_image(self, img_url: str, img_path: str) -> bool:
        """下载图片"""
        try:
            response = requests.get(img_url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(img_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
            return False
        except Exception as e:
            print(f"下载图片时出错: {str(e)}")
            return False

    def _generate_summary(self, query: str, articles: List[Dict[str, Any]]) -> str:
        """生成文章总结"""
        if not articles:
            return f"未找到关于'{query}'的有效文章。"
        
        summary = f"# 小红书'{query}'话题内容总结\n\n"
        summary += f"## 概述\n\n"
        summary += f"本报告基于小红书平台搜索'{query}'关键词，共抓取了{len(articles)}篇相关笔记进行分析。\n\n"
        
        # 提取所有话题标签
        all_topics = []
        for article in articles:
            topics = article.get('topics', [])
            if isinstance(topics, list):
                all_topics.extend([t.get('name') for t in topics if isinstance(t, dict) and 'name' in t])
        
        # 统计话题出现频率
        topic_counts = {}
        for topic in all_topics:
            if topic:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # 添加热门话题
        if topic_counts:
            summary += f"## 热门话题\n\n"
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics[:5]:  # 只显示前5个热门话题
                summary += f"- #{topic}: {count}篇笔记\n"
            summary += "\n"
        
        summary += f"## 文章列表\n\n"
        for i, article in enumerate(articles, 1):
            summary += f"### {i}. {article['title']}\n"
            summary += f"- 作者: {article['author']}\n"
            summary += f"- 点赞: {article['likes']}\n"
            
            # 添加创建时间（如果有）
            if article.get('created_time'):
                summary += f"- 发布时间: {article['created_time']}\n"
            
            # 添加笔记链接
            summary += f"- 链接: {article['url']}\n"
            
            # 添加话题标签
            topics = article.get('topics', [])
            if topics:
                topic_names = [t.get('name') for t in topics if isinstance(t, dict) and 'name' in t]
                if topic_names:
                    summary += f"- 话题: {', '.join(['#'+t for t in topic_names])}\n"
            
            # 添加内容摘要（取前200个字符）
            content_preview = article['content'][:200] + "..." if len(article['content']) > 200 else article['content']
            summary += f"- 摘要: {content_preview}\n\n"
            
            # 添加图片路径
            if article.get('images'):
                summary += f"- 图片数量: {len(article['images'])}\n"
                for j, img_path in enumerate(article['images']):
                    summary += f"  - 图片{j+1}: {img_path}\n"
                summary += "\n"
        
        # 内容分析部分
        summary += f"## 内容分析\n\n"
        summary += f"通过对以上{len(articles)}篇笔记的分析，可以得出以下关于'{query}'的主要观点和趋势：\n\n"
        
        # 分析内容长度
        content_lengths = [len(article['content']) for article in articles]
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        summary += f"1. 平均内容长度: {avg_length:.0f}字符\n"
        
        # 分析点赞情况
        try:
            likes_values = []
            for article in articles:
                likes = article['likes']
                if likes and likes != "未知":
                    # 尝试将点赞数转换为整数
                    try:
                        likes_value = int(likes.replace('k', '000').replace('w', '0000').replace('+', ''))
                        likes_values.append(likes_value)
                    except:
                        pass
            
            if likes_values:
                avg_likes = sum(likes_values) / len(likes_values)
                max_likes = max(likes_values)
                summary += f"2. 平均点赞数: {avg_likes:.0f}\n"
                summary += f"3. 最高点赞数: {max_likes}\n"
        except:
            pass
        
        summary += f"4. 这些文章主要关注{query}的哪些方面\n"
        summary += f"5. 用户对{query}的普遍评价和态度\n\n"
        
        summary += f"## 总结\n\n"
        summary += f"小红书平台上关于'{query}'的内容丰富多样，用户普遍关注...(根据实际内容补充)\n\n"
        summary += f"报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return summary

    def _save_summary(self, summary: str, save_path: str, query: str, articles: List[Dict[str, Any]]) -> str:
        """保存总结到Word文档"""
        # 检查是否可以创建Word文档
        if not DOCX_AVAILABLE:
            raise ToolError("无法创建Word文档，请安装必要的库: pip install python-docx")
            
        # 确保保存路径存在
        os.makedirs(save_path, exist_ok=True)
        
        # 从summary中提取文章信息
        import re
        article_count_match = re.search(r'共抓取了(\d+)篇相关笔记', summary)
        article_count = int(article_count_match.group(1)) if article_count_match else len(articles)
        
        # 生成文件名（使用当前时间戳避免重名）
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"小红书_{query}_总结_{timestamp}.docx"
        file_path = os.path.join(save_path, filename)
        
        try:
            # 创建新的Word文档
            doc = docx.Document()
            
            # 设置文档标题
            title = doc.add_heading(f"小红书'{query}'话题内容总结", level=0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 添加基本信息
            doc.add_paragraph(f"搜索关键词: {query}")
            doc.add_paragraph(f"抓取文章数: {article_count}篇")
            doc.add_paragraph(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            doc.add_paragraph()  # 空行
            
            # 将markdown内容转换为Word格式
            # 分割markdown内容为各个部分
            sections = summary.split('##')
            
            for section in sections[1:]:  # 跳过第一部分(标题)
                if not section.strip():
                    continue
                    
                # 处理每个部分
                lines = section.strip().split('\n')
                section_title = lines[0].strip()
                section_content = '\n'.join(lines[1:]).strip()
                
                # 添加部分标题
                doc.add_heading(section_title, level=1)
                
                # 添加部分内容
                for paragraph in section_content.split('\n\n'):
                    if not paragraph.strip():
                        continue
                        
                    # 检查是否为文章条目（以"###"开头）
                    if paragraph.strip().startswith('###'):
                        article_lines = paragraph.strip().split('\n')
                        article_title = article_lines[0].replace('###', '').strip()
                        doc.add_heading(article_title, level=2)
                        
                        # 处理文章详情
                        for detail_line in article_lines[1:]:
                            if detail_line.strip():
                                # 检查是否包含图片路径
                                img_match = re.search(r'图片\d+: (.+\.(?:jpg|png|jpeg))', detail_line)
                                if img_match and os.path.exists(img_match.group(1)):
                                    # 添加文字部分
                                    p = doc.add_paragraph(re.sub(r'图片\d+: .+\.(?:jpg|png|jpeg)', '', detail_line).strip())
                                    # 添加图片
                                    try:
                                        doc.add_picture(img_match.group(1), width=Inches(5))
                                    except Exception as e:
                                        p.add_run(f"\n[无法添加图片: {str(e)}]")
                                else:
                                    doc.add_paragraph(detail_line.strip())
                    else:
                        # 普通段落
                        # 检查是否包含图片路径
                        img_match = re.search(r'图片\d+: (.+\.(?:jpg|png|jpeg))', paragraph)
                        if img_match and os.path.exists(img_match.group(1)):
                            # 添加文字部分
                            p = doc.add_paragraph(re.sub(r'图片\d+: .+\.(?:jpg|png|jpeg)', '', paragraph).strip())
                            # 添加图片
                            try:
                                doc.add_picture(img_match.group(1), width=Inches(5))
                            except Exception as e:
                                p.add_run(f"\n[无法添加图片: {str(e)}]")
                        else:
                            doc.add_paragraph(paragraph.strip())
            
            # 添加文章图片附录
            if any('images' in article and article['images'] for article in articles):
                doc.add_heading("图片附录", level=1)
                
                for i, article in enumerate(articles, 1):
                    if 'images' in article and article['images']:
                        doc.add_heading(f"文章 {i}: {article['title']}", level=2)
                        
                        for j, img_path in enumerate(article['images'], 1):
                            if os.path.exists(img_path):
                                try:
                                    p = doc.add_paragraph(f"图片 {j}:")
                                    doc.add_picture(img_path, width=Inches(6))
                                except Exception as e:
                                    p.add_run(f"\n[无法添加图片: {str(e)}]")
            
            # 保存文档
            doc.save(file_path)
            print(f"总结报告已保存至: {file_path}")
            
            return file_path
        except Exception as e:
            raise ToolError(f"保存Word文档时出错: {str(e)}")