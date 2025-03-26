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

def load_resume_from_config(config_file="resume_config.json"):
    """从配置文件加载简历信息并格式化成字符串"""
    try:
        # 检查配置文件是否存在
        if not os.path.exists(config_file):
            print(f"警告: 简历配置文件 {config_file} 不存在! 请创建该文件并正确配置简历信息。")
            return None
        
        # 读取配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 开始构建格式化的简历文本
        resume_text = f"""
# {config.get('title', '个人简历')}
**电话**：{config.get('personal_info', {}).get('phone', '')}  
**邮箱**：{config.get('personal_info', {}).get('email', '')}  
**现居城市**：{config.get('personal_info', {}).get('city', '')}  
**微信**：{config.get('personal_info', {}).get('wechat', '')}  
**年龄**：{config.get('personal_info', {}).get('age', '')}  
**当前状态**：{config.get('personal_info', {}).get('status', '')}  
**求职意向**：{config.get('personal_info', {}).get('job_intention', '')}

## 专业技能
"""
        # 添加技能列表
        for i, skill in enumerate(config.get('skills', []), 1):
            resume_text += f"{i}. {skill}\n"
            
        # 添加教育经历
        education = config.get('education', {})
        resume_text += f"""
## 教育经历
**{education.get('university', '')}** - {education.get('major', '')} {education.get('degree', '')} {education.get('school', '')} {education.get('period', '')}
证书：{', '.join(education.get('certificates', []))}

## 工作经历
"""
        # 添加工作经历
        for i, job in enumerate(config.get('work_experience', []), 1):
            resume_text += f"{i}. **{job.get('company', '')}** - {job.get('position', '')} "
            if 'department' in job:
                resume_text += f"{job.get('department', '')} "
            resume_text += f"{job.get('period', '')}\n"
            
            # 添加工作职责
            for resp in job.get('responsibilities', []):
                resume_text += f"    - {resp}\n"
        
        # 添加项目经验
        resume_text += "\n## 项目经验\n"
        for project in config.get('projects', []):
            resume_text += f"### {project.get('name', '')} - {project.get('position', '')} {project.get('period', '')}\n"
            
            # 项目描述
            resume_text += f"#### 项目描述\n{project.get('description', '')}\n"
            
            # 项目架构 (如果有)
            if 'architecture' in project:
                resume_text += f"#### 项目架构\n{project.get('architecture', '')}\n"
            
            # 工作职责 (如果有)
            if 'responsibilities' in project:
                resume_text += "#### 工作职责\n"
                if isinstance(project['responsibilities'], list):
                    for i, resp in enumerate(project['responsibilities'], 1):
                        resume_text += f"{i}. {resp}\n"
                else:
                    resume_text += f"{project['responsibilities']}\n"
            
            # 技术要点及成果
            if 'achievements' in project:
                resume_text += "#### 技术要点以及成果\n"
                for i, achievement in enumerate(project.get('achievements', []), 1):
                    resume_text += f"{i}. {achievement}\n"
            
        return resume_text
        
    except json.JSONDecodeError:
        print(f"错误: 简历配置文件 {config_file} 格式不正确! 请检查JSON格式。")
        return None
    except Exception as e:
        print(f"加载简历配置文件时出错: {str(e)}")
        return None

# 从配置文件加载简历
resume = load_resume_from_config()

# 如果加载失败，使用一个简单的默认简历
if resume is None:
    print("警告: 使用默认简历内容。请正确配置resume_config.json文件以使用完整简历。")
    resume = """
# 简历
**姓名**: 张长龙
**电话**: 13824794702
**职位**: 后端开发工程师

## 专业技能
1. Java, Spring Boot
2. Python, Go
3. MySQL, Redis, MongoDB

## 工作经历
1. 后端开发工程师经验3年
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