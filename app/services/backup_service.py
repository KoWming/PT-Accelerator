import logging
import requests
import os
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BackupService:
    """WebDav备份服务"""
    
    def __init__(self):
        pass

    def test_connection(self, url: str, username: str = None, password: str = None) -> bool:
        """测试WebDav连接"""
        try:
            if not url:
                return False
            
            # 确保URL以/结尾，某些服务器可能需要
            if not url.endswith('/'):
                url += '/'
                
            auth = None
            if username and password:
                auth = (username, password)
            
            # 使用PROPFIND方法测试连接，这是WebDav的标准方法
            response = requests.request('PROPFIND', url, auth=auth, timeout=10)
            
            # 207 Multi-Status 是WebDav成功的典型响应
            # 200 OK 也是可能的
            if response.status_code in [200, 207]:
                return True
            
            logger.warning(f"WebDav连接测试失败: HTTP {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"WebDav连接测试出错: {str(e)}")
            return False

    def delete_file(self, url: str, auth: tuple = None) -> bool:
        """删除WebDav上的文件"""
        try:
            response = requests.delete(url, auth=auth, timeout=10)
            if response.status_code in [200, 204]:
                return True
            logger.warning(f"删除文件失败: {url}, HTTP {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"删除文件出错: {url}, {str(e)}")
            return False

    def backup_config(self, config: Dict[str, Any], file_path: str = "config/config.yaml") -> bool:
        """备份配置文件到WebDav"""
        try:
            backup_config = config.get("backup", {})
            if not backup_config.get("enable"):
                logger.info("备份功能未启用，跳过备份")
                return False

            url = backup_config.get("webdav_url")
            username = backup_config.get("webdav_username")
            password = backup_config.get("webdav_password")

            if not url:
                logger.error("WebDav URL未配置")
                return False

            if not os.path.exists(file_path):
                logger.error(f"配置文件不存在: {file_path}")
                return False

            # 构造备份文件名: config_YYYYMMDD_HHMMSS.yaml
            filename = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            
            # 确保URL以/结尾
            # 确保URL以/结尾
            if not url.endswith('/'):
                url += '/'
            
            # 尝试自动创建目录结构 (简单处理，只尝试创建最后一级目录)
            # Jianguoyun等WebDav服务如果目录不存在，PUT会报404
            # 我们先尝试检查目录是否存在，或者直接尝试创建
            
            # 解析URL，获取父目录
            # 例如 https://dav.jianguoyun.com/dav/backup/ -> 尝试 MKCOL https://dav.jianguoyun.com/dav/backup/
            try:
                # 发送 MKCOL 请求尝试创建目录
                # 如果目录已存在，通常返回 405 Method Not Allowed，这是可以接受的
                requests.request('MKCOL', url, auth=auth, timeout=10)
            except Exception:
                # 忽略创建目录的错误，继续尝试上传
                pass

            target_url = url + filename
            
            auth = None
            if username and password:
                auth = (username, password)

            with open(file_path, 'rb') as f:
                data = f.read()
                
            response = requests.put(target_url, data=data, auth=auth, timeout=30)
            
            if response.status_code in [200, 201, 204]:
                try:
                    backup_count = int(backup_config.get("backup_count", 5))
                    if backup_count > 0:
                        backups = self.list_backups(config)
                        if len(backups) > backup_count:
                            # backups is already sorted by filename descending (newest first)
                            # Remove the oldest ones
                            to_delete = backups[backup_count:]
                            for backup in to_delete:
                                file_url = backup['url']
                                logger.info(f"执行备份保留策略，删除旧备份: {backup['filename']}")
                                self.delete_file(file_url, auth)
                except Exception as e:
                    logger.error(f"执行备份保留策略出错: {str(e)}")
                
                logger.info(f"备份成功: {filename}")
                return True
            else:
                logger.error(f"备份失败: HTTP {response.status_code} - {response.text}")
                # 如果是404，提示可能是路径不存在
                if response.status_code == 404:
                     logger.error("提示: 404错误通常表示WebDav路径不存在。请检查URL是否正确，或者手动在WebDav服务器上创建该目录。")
                return False

        except Exception as e:
            logger.error(f"执行备份出错: {str(e)}")
            return False

    def list_backups(self, config: Dict[str, Any]) -> list:
        """获取WebDav上的备份文件列表"""
        try:
            backup_config = config.get("backup", {})
            url = backup_config.get("webdav_url")
            username = backup_config.get("webdav_username")
            password = backup_config.get("webdav_password")

            if not url:
                return []

            if not url.endswith('/'):
                url += '/'

            auth = None
            if username and password:
                auth = (username, password)

            # PROPFIND request
            headers = {'Depth': '1'}
            response = requests.request('PROPFIND', url, auth=auth, headers=headers, timeout=10)
            
            if response.status_code not in [200, 207]:
                logger.error(f"获取备份列表失败: HTTP {response.status_code}")
                return []

            # Parse XML
            import xml.etree.ElementTree as ET
            # Handle namespaces
            namespaces = {'d': 'DAV:'}
            
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError:
                # Try without namespace if default fails, or handle different server responses
                logger.warning("XML解析失败，尝试忽略命名空间")
                # Simple fallback: regex or just return empty if complex
                return []

            backups = []
            for response_node in root.findall('.//d:response', namespaces):
                href = response_node.find('.//d:href', namespaces).text
                propstat = response_node.find('.//d:propstat', namespaces)
                if propstat:
                    prop = propstat.find('.//d:prop', namespaces)
                    if prop:
                        displayname_node = prop.find('.//d:displayname', namespaces)
                        lastmodified_node = prop.find('.//d:getlastmodified', namespaces)
                        contentlength_node = prop.find('.//d:getcontentlength', namespaces)
                        resourcetype_node = prop.find('.//d:resourcetype', namespaces)
                        
                        # Skip directories
                        if resourcetype_node is not None and resourcetype_node.find('.//d:collection', namespaces) is not None:
                            continue

                        filename = os.path.basename(href.rstrip('/'))
                        # If displayname exists, use it, otherwise use filename from href
                        if displayname_node is not None and displayname_node.text:
                            # Some servers return full path in displayname
                            filename = os.path.basename(displayname_node.text)
                        
                        # Filter for config backups
                        if not filename.startswith('config_') or not filename.endswith('.yaml'):
                            continue

                        last_modified = lastmodified_node.text if lastmodified_node is not None else ""
                        size = contentlength_node.text if contentlength_node is not None else "0"
                        
                        backups.append({
                            "filename": filename,
                            "last_modified": last_modified,
                            "size": size,
                            "url": url + filename # Construct full URL for restoration
                        })

            # Sort by filename (date) descending
            backups.sort(key=lambda x: x['filename'], reverse=True)
            return backups

        except Exception as e:
            logger.error(f"获取备份列表出错: {str(e)}")
            return []

    def restore_backup(self, config: Dict[str, Any], filename: str, file_path: str = "config/config.yaml") -> bool:
        """从WebDav恢复备份"""
        try:
            backup_config = config.get("backup", {})
            url = backup_config.get("webdav_url")
            username = backup_config.get("webdav_username")
            password = backup_config.get("webdav_password")

            if not url:
                return False

            if not url.endswith('/'):
                url += '/'
            
            target_url = url + filename
            
            auth = None
            if username and password:
                auth = (username, password)

            response = requests.get(target_url, auth=auth, timeout=30)
            
            if response.status_code == 200:
                # Verify content is valid yaml
                import yaml
                try:
                    yaml.safe_load(response.content)
                except yaml.YAMLError:
                    logger.error("恢复失败: 备份文件不是有效的YAML格式")
                    return False

                # Write to config file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"成功从 {filename} 恢复配置")
                return True
            else:
                logger.error(f"恢复失败: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"执行恢复出错: {str(e)}")
            return False
