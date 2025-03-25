# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import sys
import json
import re

from deepseek import chat

resume = """
# 张长龙个人简历
**电话**：13824794702  
**邮箱**：louisgagaheehee@gmail.com  
**现居城市**：深圳市  
**微信**：13824794702  
**年龄**：27岁  
**当前状态**：在职  
**求职意向**：后端开发

## 专业技能
1. 掌握Java基础知识，涵盖集合、反射、多线程、线程池、锁以及基本数据结构。熟悉JVM内存模型、内存管理、ZGC、三色标记法等回收算法，以及G1、CMS等常见垃圾收集器，了解JVM调优，有解决对象提前晋升调优经验。
2. 熟悉SpringBoot、SpringMVC、Mybatis等开源框架，了解SpringCloud Alibaba微服务组件，熟悉服务治理、熔断降级、负载均衡相关知识。
3. 掌握Golang基础知识，拥有基于Go语言开发分布式系统的经验，深入理解Go的并发模型（goroutines和channels），并能有效设计高并发、高性能的分布式服务。
4. 掌握Python编程，具有AIGC领域的应用开发经验，掌握提示工程及多模态输入处理。具备AI工作流设计及Agent开发能力，拥有构建会话式RAG服务的实战经验。
5. 熟悉MySQL、PostgreSQL，熟悉B+树索引特点、事务以及常见优化手段，了解MVCC多版本并发控制原理、三大日志及其作用，有过冷热分离、数据迁移、大数据量处理、慢SQL优化、索引优化等实操经验。
6. 熟悉MongoDB，掌握其应用场景，基于MongoDB Atlas实现文档向量化存储，了解慢查询优化基本手段以及主从、集群等高可用方案。
7. 熟练掌握Redis数据结构、应用场景、持久化与过期及内存淘汰策略。熟悉多路复用、Cluster模式与扩缩容，能处理缓存一致性、热/大key问题。了解Raft、Gossip及一致性哈希，熟悉分布式锁，研读过Redisson相关源码。
8. 掌握Kubernetes基本应用场景以及底层原理，如基本组件、网络通信模型、数据卷挂载机制，了解其服务发现、负载均衡、服务保活、容器资源调度等机制，熟悉常用的Kubectl客户端命令。
9. 掌握Docker容器化开发，独立编写多阶段Dockerfile构建应用镜像，通过本地容器部署调试后端服务，运用Docker Compose编排开发环境组件，集成CI实现自动化构建，具备容器网络配置实践经验。
10. 了解ElasticSearch分布式搜索引擎，了解倒排索引、分词器以及滚动查询，熟悉其基本使用场景。
11. 熟悉Google Pub/Sub、Kafka消息中间件基本设计思想以及应用场景。熟悉消息积压、防重、防丢、削峰填谷等常规解决方案。熟悉消息的可靠投递、顺序消费。了解顺序写入、零拷贝等性能优化场景。

## 教育经历
**广东海洋大学** - 计算机科学与技术 本科 数学与计算机学院 2017年09月 - 2021年06月
证书：CET - 4

## 工作经历
1. **深圳市逻辑控股科技有限公司** - 后端开发工程师 2022年12月 - 至今
    - 从0到1负责Nova App的后端系统设计、开发、部署、上线。参与社交、Mining等核心功能的开发。参与对系统进行优化降本、代码逻辑重构、文档输出等工作。
    - 从0到1负责RAG AI对话服务的后端系统设计，开发。
2. **深圳市云歌人工智能技术有限公司** - 服务端开发工程师 产品研发部 2022年07月 - 2022年11月
    - 负责灵鸽APP投递服务以及消息中心服务的开发、日常迭代，功能模块的重构以及日常维护，主导消息中心服务的设计与开发，与PC/移动客户端的联调与对接。
3. **萨摩耶数字科技有限公司** - 数据科学工程师(Java) 数据业务部 2021年06月 - 2022年07月
    - 负责天心系统、渠道管理系统、以及Canal中间件的日常开发与维护，需求评审与Code Review，以及对生产问题的排查与解决。
4. **深圳市TCL新技术有限公司** - 后端开发实习生 云平台 鸿鹄实验室 2020年11月 - 2021年03月
    - 了解企业开发流程，参与基本的表设计与功能模块开发。

## 项目经验
### ChatBooster - 后端开发工程师 2024年07月 - 至今
#### 项目描述
ChatBooster是一款企业赋能平台，整合WhatsApp、Facebook、Instagram等多渠道资源，为企业构建一站式解决方案，助力业绩提升。平台借助RAG AI技术，提升客户支持效率，运用自动化对话式AI增强客户互动体验。同时，基于Pixel精准追踪广告投放关键事件，深度解析转化率数据，为优化广告投放策略提供数据支撑，实现广告效果最大化与精细化管理。
#### 工作职责
1. 从0到1负责调研Langchain、Huggingface等相关技术栈，设计并搭建RAG应用程序。
2. 搭建短链系统，基于埋点和用户画像反哺营销策略和广告投放方案。
#### 项目架构
基于Golang+Kratos构建核心服务，数据层采用Gorm/MySQL+Redis缓存，Protocol定义通信协议。集成GCP Pub/Sub异步消息队列与Cloud Storage对象存储，DevOps链涵盖GCP代码托管、CI/CD流水线、K8s编排及监控告警模块，保障高可用与弹性扩展。
#### 技术要点以及成果
1. 人力成本缩减15%，人工接管率稳定<15%，释放40%客服人力转向高价值业务。
2. 通过AI Agent实现语义分析及意图识别，预设多场景回复策略，AI自主判断用户意图并匹配回复方案，以预设话术及人工服务兜底，覆盖68%的常见场景，显著降低人工服务压力。
3. 集成Gemini多模态AI引擎，实现Text+Audio+Image To Text统一解析，支持多语言识别（含小语种/方言，准确率>90%）及情绪分析，图片识别准确率>90%，扩展复杂业务场景处理能力，通过多模态语义理解提升意图识别准确率，结合上下文对话管理优化交互体验。
4. 集成DeepSeek深度思考模型，针对中文语境优化语义理解与意图识别，提升中文对话交互精准度，结合上下文理解与多轮对话管理，显著增强复杂中文场景处理能力，中文意图识别准确率高达90%以上。
5. 设计并实现多平台大语言模型的Prompt工程化，设计基于角色预设与知识约束的动态Prompt模板，构建支持图文跨模态的动态模板，基于RAGAs等工具构建自动化评估框架，结合人工标注，量化问答相关性（92%）与准确性（85%），迭代优化幻觉率20%降至9%。
6. 集成DuckDuckGoSearch API实现联网检索，通过LLM动态调用搜索引擎获取最新资讯，结合语义分析与数据摘要生成时效性回答，支持科技、金融等多领域实时查询。
7. 依托MongoDB构建1536维向量库，采用BM25+余弦相似度混合检索（权重比6:4），文档召回率达90%以上。
8. 设计租户隔离方案，并实现基于特定知识库范围的精准AI问答功能，保障多客户环境下的数据隐私与应用灵活性。
9. 实现短链功能，基于埋点统计UV/PV及渠道来源以及收集用户画像，反哺广告投放策略以及驱动营销策略优化，识别高转化渠道提升ROI，获客成本降低25%。

### Nova App - 后端开发工程师 2022年12月 - 2024年06月
#### 项目描述
一款基于社交+Mining的面向海外用户产品。用户可在App上发表动态获得Nova Token，并每日进行一次Mining操作，24小时后结算Nova Token。项目上线后在两周内注册用户达到25万人，业务增长迅速，平均日活超过20w以上。
#### 项目架构
以Java+Spring为核心，采用Spring Boot基本框架。并基于Google Cloud Platform及Kubernetes进行部署与运维，借助Mysql+MongoDB作持久层存储中间件、ES为搜索引擎、Redis为应用缓存。通过Cloud Flare实现限流、安防及网关层缓存与流量网关，Feign作RPC框架，消息中间件选Google Pub/Sub，引入Firebase实现用户系统等。
#### 工作职责
对Nova后端账户模块、社交模块、Mining模块进行包括但不限于业务逻辑重构和优化、功能开发与迭代、服务性能优化、数据库性能优化。保证数据在长链路流转的过程中的可靠性和一致性。
#### 技术要点以及成果
1. 参与实现feed流，对用户following data功能基于redis的zset重构，对following data提前聚合，相关接口响应时间提高300%，避免了数据读扩散现象。
2. 在业务快速增长阶段对数据库的索引、慢SQL、以及引入cloudflare缓存+限流进行优化，系统性能整体提升30%以上。
3. 设计并实现贴文敏感词过滤以及敏感视频检测，检测成功率达99%。
4. 参与Mining功能的重构和优化，以延时任务+消息队列的形式替换定时任务方案，将集中的数据库压力分散，提高数据库可用性，数据实时性提高50%。
5. 设计并实现基于区域推荐的机制，以排行榜的形式实时更新区域热贴排行榜。
6. 基于消息队列异步解耦，缓解用户关注、取关、点赞等社交行为带来的写扩散问题，服务吞吐量提升。
7. 基于Firebase快速设计并实现通知推送服务、以及账户登录注册、第三方社交账号绑定。
8. 从0到1负责app对应后台管理系统的实现，包括但不限于用户数据统计、贴文管理、评论管理等等。

### 灵鸽App 2022年07月 - 2022年11月
#### 项目描述
灵鸽主要服务于猎头与用户，业务范围定位在高端人才招聘，通过猎头找用户、猎头邀请用户的模式为企业去寻找合适的候选人。
#### 项目架构
以SpringBoot为基本框架，使用MySql、ES作为持久层数据库，以Redis作为缓存层，采用Kubernates+容器化进行部署并配合Nacos作为注册中心，以Ingress-Naginx作为流量网关，以Dubbo作为RPC框架，配置中心采用Apoll，消息中间件采用RocketMQ。
#### 工作职责
1. 对投递服务历史项目进行迁移逻辑重构、性能优化，对需求进行分析以及方案设计。
2. 主导消息中心服务的功能模块设计、数据存储设计以及性能优化与迭代。
3. 业务问题的排查、定位与解决。
#### 技术要点以及成果
1. 对猎头推荐信息查询接口进行优化以及重构，接口RT优化300%。
2. 设计消息已读未读存储方案，减少80%消息状态数据存储量。
3. 基于Redis有序集合缓存热点消息如系统消息，基于哈希结构缓存消息已读未读状态，提高高频接口查询响应速度。
4. 基于时间范围进行限制，优化全量已读消息的场景，避免慢查询发生。
5. 优化红点未读消息统计逻辑，基于MQ由全量统计变增量统计，优化接口RT，并以调度任务进行数据一致性兜底。
6. 对慢SQL进行索引优化，使得查询效率提高60%。
7. 基于openCV实现自动化测试解决方案（基于图像识别的验证码处理模块），成功率达95%以上。

### 天心系统 2021年06月 - 2022年07月
#### 项目描述
将贷后业务、风控、管理、运营集为一体的科技产品，其模块有智能分案、催收作业主流程、用户排班、渠道管理、工单模块、风险指标监控、外包模块、内部论坛、内部聊天。负责公司的风险指标监控，如入催率、逾期率、逾期金额、坏账风险、回收率等，同时对逾期用户进行智能化催收，系统主要面向内部催收人员以及业务人员使用。每年可为公司催回数亿借贷款，一定程度保障公司的现金流。
#### 系统架构
以SSM为基本框架，主要使用Mysql、Redis、ES作为数据库选型，消息中间件使用Kafka进行消息通信，同时使用Sentinel保证整体高可用。
#### 工作职责
1. 参与需求设计评审、代码评审以及与业务方进行需求讨论以及调整。
2. 对于功能模块的设计、以及重构已有的系统模块，如聊天模块、论坛模块等。
3. 对系统生产问题的排查、定位以及提供解决方案，如解决自动语音外呼异常、数据跑批异常等。
4. 系统性能方面优化，如慢SQL优化等，使得系统可用时间达99%以上。
#### 技术要点以及成果
1. 优化亿级数据处理手段，利用索引解决深度分页的问题，并且将处理时间由20h优化至3h。
2. 优化语音外呼任务，实现系统外呼渠道切换自动化并实现加权随机轮询算法，提高容错性以及伸缩性。
3. 优化用户操作日志的存储以及查询速度，并根据规则统计用户的闲置时间。
4. 利用Canal+MQ对客户还款金额的更新延迟由20分钟优化至准实时1 - 5秒。
5. 通过策略模式以与工厂模式及反射实现风控策略的懒加载，提升项目启动速度，并使代码更优雅。
6. 通过定时任务以及拦截器日志埋点，解决用户session无法过期导致长时间占用连接的问题。
7. 基于ES进行数据冷热分离，优化业务查询场景性能，使热数据查询速度提高80%，冷数据查询提高30%。
8. 通过对JVM调参，解决系统因对象提前晋升至老年代导致频繁Full GC而内存溢出的问题。
9. 根据业务场景参与优化慢SQL、数据表优化，系统整体查询性能提升20%。
10. 对群聊模块进行重构，实现修改用户信息后自动退出、进入对应的群，省去维护群聊的人力时间。

### 渠道管理系统 2021年06月 - 2022年07月
#### 项目描述
天心系统的前置系统，从核心系统拉取数据并预处理。负责天心系统几十万入催客户的处理，包括前置数据整理、前置系统跑批、转发客户实时还款信息。迭代与维护跑批预处理逻辑、账户核心系统客户数据等。
#### 技术要点
1. 负责项目的日常迭代与维护。
2. 对接渠道进行客户账款消息上送至其他系统。
3. 通过SQL拆分以及优化慢SQL，对数据跑批时间进行优化，使得跑批时间减少30%。
4. 生产问题的排查与提供解决方案。

### Canal中间件 2021年06月 - 2022年07月
#### 项目描述
阿里巴巴旗下开源中间件，主要用途是基于MySQL数据库增量日志解析，提供增量数据订阅和消费，通过公司研发的中间层dcs，将同步数据分发至各个从库。
#### 工作职责
负责系统日常业务工作、问题处理，协调各个开发部门的数据同步工作。
#### 技术要点
1. 参与了公司Canal分布式部署的高可用方案的设计，并与运维集成至公司发布平台。
2. 公司Canal中间件的日常维护以及实例配置更新。
3. 参与解决数据同步丢失等生产问题的排查与解决。
4. 参与公司数据库迁移后的数据同步、数据恢复工作，保证了数据的0丢失。
"""

def extract_salary_from_api(driver):
    """从已发生的网络请求中提取job detail API响应数据"""
    try:
        print("\n尝试提取职位详情API数据...")
        
        # 获取性能日志
        logs = driver.get_log('performance')
        
        # 提取包含 detail.json 请求的响应
        detail_requests = []
        
        # 首先查找所有包含目标API的请求
        for log in logs:
            try:
                log_entry = json.loads(log["message"])
                
                # 检查是否为网络响应
                if ("Network.responseReceived" in log_entry["message"]["method"] or 
                    "Network.loadingFinished" in log_entry["message"]["method"]):
                    
                    # 获取请求URL (有些日志可能没有URL信息)
                    if "params" in log_entry["message"] and "response" in log_entry["message"]["params"]:
                        request_url = log_entry["message"]["params"]["response"].get("url", "")
                        
                        # 检查是否为目标API
                        if "wapi/zpgeek/job/detail.json" in request_url:
                            detail_requests.append({
                                "request_id": log_entry["message"]["params"]["requestId"],
                                "url": request_url
                            })
            except Exception as log_error:
                # 忽略单个日志处理错误，继续下一个
                continue
        
        # 如果找到多个匹配的请求，取最新的一个（通常是最后一个）
        if detail_requests:
            # 按照日志中出现的顺序，最后一个通常是最新的
            latest_request = detail_requests[-1]
            print(f"\n找到职位详情API请求: {latest_request['url']}")
            
            # 获取响应内容
            try:
                # 尝试使用CDP命令获取响应体
                response = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": latest_request["request_id"]})
                
                if response and "body" in response:
                    # 解析JSON响应
                    json_data = json.loads(response["body"])
                    
                    # 打印完整的响应体结构，包含主要内容
                    print("\n========== 职位详情API响应主要内容 ==========")
                    
                    # 检查响应码，确认请求成功
                    if json_data.get("code") == 0 and "zpData" in json_data and "jobInfo" in json_data["zpData"]:
                        zp_data = json_data["zpData"]
                        job_info = zp_data["jobInfo"]
                        company_info = zp_data["brandComInfo"] if "brandComInfo" in zp_data else {}
                        boss_info = zp_data["bossInfo"] if "bossInfo" in zp_data else {}
                        
                        # 打印职位基本信息
                        print("\n【职位基本信息】")
                        print(f"职位名称: {job_info.get('jobName', '未知')}")
                        print(f"薪资范围: {job_info.get('salaryDesc', '未知')}")
                        print(f"工作地点: {job_info.get('locationName', '未知')}")
                        print(f"详细地址: {job_info.get('address', '未知')}")
                        print(f"工作经验: {job_info.get('experienceName', '未知')}")
                        print(f"学历要求: {job_info.get('degreeName', '未知')}")
                        
                        # 打印技能标签
                        skills = job_info.get("showSkills", [])
                        if skills:
                            print(f"技能要求: {', '.join(skills)}")
                        
                        # 打印职位描述
                        description = job_info.get("postDescription", "")
                        if description:
                            print("\n【职位描述】")
                            print(description)
                        
                        # 打印招聘人信息
                        if boss_info:
                            print("\n【招聘人信息】")
                            print(f"招聘人: {boss_info.get('name', '未知')} ({boss_info.get('title', '未知')})")
                            print(f"活跃状态: {boss_info.get('activeTimeDesc', '未知')}")
                        
                        # 打印公司信息
                        if company_info:
                            print("\n【公司信息】")
                            print(f"公司名称: {company_info.get('brandName', '未知')}")
                            print(f"融资阶段: {company_info.get('stageName', '未知')}")
                            print(f"公司规模: {company_info.get('scaleName', '未知')}")
                            print(f"所属行业: {company_info.get('industryName', '未知')}")
                            
                            # 打印公司简介
                            if "introduce" in company_info:
                                print("\n【公司简介】")
                                print(company_info.get("introduce", ""))
                            
                            # 打印公司福利
                            benefits = company_info.get("labels", [])
                            if benefits:
                                print(f"\n【公司福利】: {', '.join(benefits)}")
                        
                        print("\n========== 职位详情API响应内容结束 ==========")
                        
                        # 返回职位薪资和完整信息
                        job_details = {
                            "salary": job_info.get("salaryDesc", ""),
                            "jobName": job_info.get("jobName", ""),
                            "experience": job_info.get("experienceName", ""),
                            "education": job_info.get("degreeName", ""),
                            "location": job_info.get("locationName", ""),
                            "address": job_info.get("address", ""),
                            "description": job_info.get("postDescription", ""),
                            "skills": job_info.get("showSkills", []),
                            "company": {
                                "name": company_info.get("brandName", ""),
                                "stage": company_info.get("stageName", ""),
                                "scale": company_info.get("scaleName", ""),
                                "industry": company_info.get("industryName", ""),
                                "benefits": company_info.get("labels", [])
                            }
                        }
                        
                        return job_info.get("salaryDesc", ""), job_details
                    else:
                        print(f"API响应错误: {json_data.get('message', '未知错误')}")
            except Exception as resp_error:
                print(f"获取或解析响应内容时出错: {str(resp_error)}")
                import traceback
                traceback.print_exc()
        else:
            print("未找到任何包含wapi/zpgeek/job/detail.json的网络请求")
            
            # 辅助诊断：打印找到的所有网络请求URL
            print("\n尝试列出找到的所有网络请求:")
            all_requests = []
            for log in logs:
                try:
                    log_entry = json.loads(log["message"])
                    if "Network.responseReceived" in log_entry["message"]["method"]:
                        if "params" in log_entry["message"] and "response" in log_entry["message"]["params"]:
                            url = log_entry["message"]["params"]["response"].get("url", "")
                            if url and "wapi" in url:  # 只显示API请求
                                all_requests.append(url)
                except:
                    continue
            
            if all_requests:
                print(f"找到 {len(all_requests)} 个API请求:")
                for idx, url in enumerate(all_requests[:10]):  # 只显示前10个
                    print(f"{idx+1}. {url}")
                if len(all_requests) > 10:
                    print(f"... 还有 {len(all_requests)-10} 个请求未显示")
            else:
                print("没有找到任何API请求")
        
        # 如果没有找到API响应或解析失败，返回None
        return None, None
    except Exception as e:
        print(f"提取API响应时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def setup_browser():
    """配置并启动Chrome浏览器，返回WebDriver实例"""
    print("正在配置浏览器...")
    
    # 配置Chrome选项以使用本机浏览器配置
    chrome_options = Options()

    # 避免使用已有的用户数据目录，改为创建临时目录
    # chrome_options.add_argument("--headless")  # 无头模式，取消注释可在后台运行
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")

    # 重要：启用性能日志
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    # 使用一个临时的用户目录，避免与现有Chrome冲突
    temp_user_data_dir = os.path.join(os.getcwd(), "temp_chrome_profile")
    print(f"使用临时用户数据目录: {temp_user_data_dir}")
    chrome_options.add_argument(f"user-data-dir={temp_user_data_dir}")
    
    try:
        print("正在初始化WebDriver...")
        # 使用配置好的选项创建Chrome WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver初始化成功，浏览器已打开")
        
        # 设置隐式等待时间
        driver.implicitly_wait(10)
        
        return driver
    except Exception as e:
        print(f"初始化WebDriver时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def handle_login(driver):
    """处理登录流程，返回是否登录成功"""
    print("检查登录状态...")
    try:
        # 尝试查找导航栏中的头像元素，这表示已经登录
        nav_figure = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.nav-figure'))
        )
        print("检测到头像元素，用户已经登录！")
        return True
    except:
        # 未找到头像元素，说明未登录，点击登录按钮
        print("未检测到头像元素，用户未登录，准备点击登录按钮...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[ka="header-login"]'))
        )
        login_button.click()
        print('已自动跳转到登录界面')
        
        # 自动检测用户是否完成登录（通过检查导航栏中的头像元素）
        print("等待用户完成登录...")
        login_success = False
        max_wait_time = 300  # 最长等待5分钟
        start_time = time.time()
        
        while not login_success and time.time() - start_time < max_wait_time:
            try:
                # 检查导航栏中的头像元素
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.nav-figure'))
                )
                login_success = True
                print("检测到头像元素，用户已登录成功！")
            except:
                # 如果没有找到头像元素，等待3秒后再次检查
                print("等待登录中... 已等待", int(time.time() - start_time), "秒")
                time.sleep(3)
        
        if not login_success:
            print("登录等待超时，请手动确认是否已登录")
            input("确认已登录后按回车键继续...")
            return True
        return login_success

def apply_job_filters(driver):
    """应用工作筛选条件"""
    print("尝试点击顶部的推荐按钮...")
    try:
        recommend_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[ka="header-job-recommend"]'))
        )
        recommend_button.click()
        print("成功点击推荐按钮，正在跳转到推荐页面...")
        
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        print("推荐页面加载完成，当前URL:", driver.current_url)
        
        # 选择工作经验3-5年的选项
        print("尝试选择工作经验3-5年...")
        
        # 先找到并点击工作经验下拉框
        try:
            exp_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'condition-filter-select')]/div[contains(@class, 'current-select')]/span[text()='工作经验']"))
            )
            exp_dropdown.click()
            print("成功点击工作经验下拉框")
            
            # 等待下拉菜单显示，然后点击3-5年选项
            exp_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li[ka='sel-job-rec-exp-105']"))
            )
            exp_option.click()
            print("成功选择3-5年工作经验")
            
            # 等待页面刷新并加载新的职位列表
            time.sleep(2)
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            print("筛选后的职位列表加载完成")
            
            # 选择薪资待遇20-50K
            print("尝试选择薪资待遇20-50K...")
            
            # 找到并点击薪资待遇下拉框
            salary_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'condition-filter-select')]/div[contains(@class, 'current-select')]/span[text()='薪资待遇']"))
            )
            salary_dropdown.click()
            print("成功点击薪资待遇下拉框")
            
            # 等待下拉菜单显示，然后点击20-50K选项
            salary_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li[ka='sel-job-rec-salary-406']"))
            )
            salary_option.click()
            print("成功选择20-50K薪资范围")
            
            # 等待页面刷新并加载新的职位列表
            time.sleep(2)
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            print("薪资筛选后的职位列表加载完成")
            return True
            
        except Exception as filter_error:
            print(f"设置筛选条件时出错: {str(filter_error)}")
            print("继续执行后续操作...")
            return False
    except Exception as e:
        print(f"点击推荐按钮时发生错误: {str(e)}")
        print("继续执行后续操作...")
        return False

def scroll_for_more_jobs(driver, pre_scroll_count):
    """滚动页面加载更多职位"""
    print("向下滚动加载更多职位...")
    
    # 简化的滚动逻辑：获取最后一个职位卡片并滚动到它的底部
    try:
        job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-card-wrap')
        if job_cards:
            last_visible_job = job_cards[-1]
            
            # 滚动到最后一个职位卡片的底部
            driver.execute_script("arguments[0].scrollIntoView(false);", last_visible_job)
            
            # 额外滚动以确保触发加载更多
            driver.execute_script("window.scrollBy(0, 300);")
            print("滚动到列表底部以加载更多职位...")
            
            # 等待新内容加载
            time.sleep(3)
        else:
            print("没有找到职位卡片，无法滚动")
            return False
    except Exception as scroll_error:
        print(f"滚动时出错: {str(scroll_error)}")
        # 使用JavaScript直接滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    
    # 检查是否有新的职位卡片加载
    new_job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-card-wrap')
    post_scroll_count = len(new_job_cards)
    
    print(f"滚动后找到 {post_scroll_count} 个职位卡片 (之前: {pre_scroll_count})")
    
    # 如果没有新的职位卡片加载，可能已经到达页面底部
    if post_scroll_count <= pre_scroll_count:
        print("没有更多职位可加载")
        return False
    return True

def process_job_details(driver, job_card, index):
    """处理单个职位的详情"""
    try:
        print(f"点击查看职位 {index+1} 详情...")
        
        # 滚动到当前职位卡片以确保它在视图中
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        time.sleep(0.5)  # 短暂等待滚动完成
        
        # 等待职位卡片中的链接元素可点击
        job_link = WebDriverWait(job_card, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.job-name'))
        )
        job_link.click()
        
        # 等待职位详情加载完成
        print(f"等待职位详情页面加载...")
        
        # 等待职位详情页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.job-detail-container'))
        )
        
        # 提取详情页信息
        salary, job_details = extract_salary_from_api(driver)
        
        # 可以在这里添加额外的处理逻辑
        # todo 这里需要处理
        if job_details:
            # 提取关键职位信息
            job_name = job_details.get("jobName", "")
            job_info = f"""
            职位名称: {job_name}\n
            公司名称: {job_details.get("company", {}).get("name", "")}\n
            薪资范围: {salary}\n
            工作地点: {job_details.get("city", "未指定")}\n
            所需技能: {", ".join(job_details.get("skills", []))}\n
            工作年限: {job_details.get("workYear", "未指定")}\n
            职位描述: {job_details.get("description", "")}\n
            学历要求: {job_details.get("education", "未指定")}\n
            公司信息: {job_details.get("company", {})}\n
            """
            # 打印job_info
            print("process_job_details job_info:",job_info)
            # 设计system prompt，告诉AI如何评估匹配度
            system_prompt = """你是一位专业的招聘顾问，需要评估求职者简历与职位的匹配程度。
            首先检查以下两个关键条件:
            1. 教育背景是否满足职位最低学历要求
            2. 工作经验年限是否达到职位要求的最低标准
            
            如果以上任一条件不满足，直接返回:
            {"score": 0,"analysis": "不符合基本要求","reason": "说明具体原因(学历/经验不达标)"}
            
            如果基本条件满足，请根据以下几点给出匹配度评分（满分100分）：
            1. 技能匹配度（40分）：技术栈、编程语言、框架、工具等是否匹配
            2. 经验相关度（30分）：项目经验与目标职位的相关程度
            3. 行业背景（20分）：行业经验与公司业务的契合度
            4. 教育背景（10分）：教育背景对职位的适配程度
            
            请给出详细的分析和最终的匹配分数，并且尤其重视技能和经验的匹配情况。
            只返回JSON格式数据，不要包含任何其他文本或格式，不要使用```json这种标记。
            """
            
            # 构建提示，要求评估简历与职位匹配度
            prompt = f"""请评估下面的简历与职位的匹配程度，并给出一个0-100的分数。

            ## 职位信息:
            {job_info}
            
            ## 简历:
            {resume}
            
            请以JSON格式返回结果，包含总分数和详细分析：
            {{
                "score": 数字,
                "analysis": "详细分析...",
                "skills_match": "技能匹配分析...",
                "experience_match": "经验匹配分析...",
                "industry_match": "行业匹配分析...",
                "education_match": "教育背景匹配分析..."
            }}
            """
            
            print(f"\n正在使用DeepSeek分析职位 '{job_name}' 与简历的匹配度...")
            
            # 调用DeepSeek API进行分析
            result = chat(prompt=prompt, system_prompt=system_prompt)
            
            # 打印分析结果
            print("\n===== DeepSeek分析结果 =====")
            print(result)
        return True
    except Exception as e:
        print(f'提取职位信息时发生错误: {str(e)}')
        return False

def process_job_listings(driver, max_jobs=20):
    """处理职位列表，最多处理指定数量的职位"""
    # 等待职位列表加载
    print("等待职位列表加载...")
    job_cards = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.job-card-wrap'))
    )
    print(f"找到 {len(job_cards)} 个职位卡片")
    
    jobs_processed = 0
    
    # 持续加载和处理职位直到达到预设数量
    while jobs_processed < max_jobs:
        # 重新获取当前页面上的职位卡片
        job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-card-wrap')
        print(f"当前页面上有 {len(job_cards)} 个职位卡片")
        
        # 从当前位置开始遍历职位列表
        start_index = jobs_processed
        end_index = min(len(job_cards), max_jobs)
        
        for i in range(start_index, end_index):
            try:
                # 由于页面可能已经滚动，需要重新获取元素
                job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-card-wrap')
                if i >= len(job_cards):
                    break
                
                job_card = job_cards[i]
                process_job_details(driver, job_card, i)
                
                jobs_processed += 1
                
                # 添加短暂休息以避免过快操作
                time.sleep(0.5)
                
            except Exception as e:
                print(f'处理职位卡片时发生错误: {str(e)}')
                jobs_processed += 1
                continue
        
        # 检查是否达到目标数量
        if jobs_processed >= max_jobs:
            print(f"已达到目标数量 {max_jobs} 个职位，结束处理")
            break
        
        # 所有当前可见的职位卡片都已处理，滚动页面加载更多
        print(f"已处理 {jobs_processed} 个职位，尝试加载更多...")
        
        # 记录滚动前的职位卡片数量
        pre_scroll_count = len(driver.find_elements(By.CSS_SELECTOR, '.job-card-wrap'))
        
        # 如果没有新职位加载，退出循环
        if not scroll_for_more_jobs(driver, pre_scroll_count):
            break

def main():
    """主函数，控制整个爬虫流程"""
    driver = None
    try:
        # 获取配置好的浏览器实例
        driver = setup_browser()
        
        # 访问BOSS直聘官网
        print("正在访问BOSS直聘官网...")
        driver.get('https://www.zhipin.com/')
        
        # 打印debug信息
        print("当前页面URL:", driver.current_url)
        
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        print('成功打开BOSS直聘官网')
        
        # 处理登录
        login_success = handle_login(driver)
        if not login_success:
            print("登录失败，退出程序")
            return
        
        # 登录成功后，等待页面内容加载
        print("页面内容加载中...")
        time.sleep(2)
        
        # 应用职位筛选条件
        filter_applied = apply_job_filters(driver)
        if not filter_applied:
            print("应用筛选条件失败，继续尝试处理职位列表")
        
        # 处理职位列表
        process_job_listings(driver, max_jobs=20)
        
        print("职位爬取完成！")
        
    except Exception as e:
        print(f'发生错误: {str(e)}')
        import traceback
        traceback.print_exc()
    
    finally:
        # 退出浏览器
        if driver:
            try:
                driver.quit()
                print("浏览器已关闭")
            except Exception as e:
                print(f"关闭浏览器时出错: {str(e)}")

if __name__ == "__main__":
    main()