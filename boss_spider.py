# -*- coding: utf-8 -*-
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import resume_config
from deepseek import chat


def extract_salary_from_api(driver):
    """从已发生的网络请求中提取job detail API响应数据"""
    try:
        print("\n尝试提取职位详情API数据...")
        time.sleep(1)  # 这里睡眠是因为点击后等待接口响应才能抓取到性能日志
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
                response = driver.execute_cdp_cmd("Network.getResponseBody",
                                                  {"requestId": latest_request["request_id"]})

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
                    print(f"{idx + 1}. {url}")
                if len(all_requests) > 10:
                    print(f"... 还有 {len(all_requests) - 10} 个请求未显示")
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
                EC.element_to_be_clickable((By.XPATH,
                                            "//div[contains(@class, 'condition-filter-select')]/div[contains(@class, 'current-select')]/span[text()='工作经验']"))
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
                EC.element_to_be_clickable((By.XPATH,
                                            "//div[contains(@class, 'condition-filter-select')]/div[contains(@class, 'current-select')]/span[text()='薪资待遇']"))
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
        print(f"点击查看职位 {index + 1} 详情...")
        # 滚动到当前职位卡片以确保它在视图中
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        time.sleep(0.5)  # 短暂等待滚动完成

        # 检查是否已经投递过（按钮显示"继续沟通"）
        try:
            job_button = job_card.find_element(By.CSS_SELECTOR, '.op-btn.op-btn-chat')
            button_text = job_button.text.strip()
            
            if button_text == "继续沟通":
                print(f"职位 {index + 1} 已经投递过（按钮显示'继续沟通'），跳过...")
                return True
        except:
            # 如果在卡片中找不到按钮，继续处理（可能在详情页会有按钮）
            pass

        # 等待职位卡片中的链接元素可点击
        job_link = WebDriverWait(job_card, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.job-name'))
        )
        job_link.click()

        # 等待职位详情加载完成
        print(f"等待职位 {index + 1} 详情页面加载...")

        # 等待职位详情页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.job-detail-container'))
        )

        # 提取详情页信息
        salary, job_details = extract_salary_from_api(driver)

        # 可以在这里添加额外的处理逻辑
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

            # 构建提示，要求评估简历与职位匹配度
            prompt = f"""请评估下面的简历与职位的匹配程度，并给出一个0-100的分数。

            ## 职位信息:
            {job_info}

            ## 简历:
            {resume_config.resume_content}

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
            result = chat(prompt=prompt, system_prompt=resume_config.system_prompt)

            # 打印分析结果
            print(f"\n===== DeepSeek'{job_name}'分析结果 analysis result =====")
            print(result)
            
            # 解析JSON结果并提取分数
            try:
                result_json = json.loads(result)
                score = result_json.get("score", 0)

                # 如果分数大于85，调用投递函数
                if score >= 85:
                    print(f"职位 '{job_name}' 匹配分数高于85，尝试投递...")
                    apply_for_job(driver, job_name, score)
                else:
                    print(f"职位匹配分数较低，不予投递: {score}")
            except json.JSONDecodeError:
                print("无法解析DeepSeek返回的JSON结果")
            except Exception as json_error:
                print(f"处理分析结果时出错: {str(json_error)}")
        return True
    except Exception as e:
        print(f'提取职位信息时发生错误: {str(e)}')
        return False


def apply_for_job(driver, job_name, score):
    """
    投递职位申请函数
    """
    try:
        print(f"准备投递职位 '{job_name}' (匹配分数: {score})...")
        
        # 查找沟通按钮
        chat_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.op-btn.op-btn-chat'))
        )
        
        # 检查按钮文案，判断是否已经投递过
        button_text = chat_button.text.strip()
        if button_text == "继续沟通":
            print(f"职位 '{job_name}' 已经投递过（按钮显示'继续沟通'），跳过投递")
            return True
        
        # 确认是"立即沟通"按钮，可以投递
        if button_text == "立即沟通":
            # 点击"立即沟通"按钮
            chat_button.click()
            print(f"已点击'立即沟通'按钮，投递职位...")
            
            # 等待弹出对话框出现
            print("等待确认对话框出现...")
            time.sleep(1)
            try:
                # 等待"留在此页"按钮出现
                stay_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.greet-boss-footer .cancel-btn'))
                )
                print("找到'留在此页'按钮，准备点击...")
                
                # 点击"留在此页"按钮
                stay_button.click()
                print("已点击'留在此页'按钮，完成投递流程")
                
                # 打印成功信息
                print(f"成功投递职位: '{job_name}' (匹配分数: {score})")
                return True
            except Exception as dialog_error:
                print(f"处理确认对话框时出错: {str(dialog_error)}")
                return False
        else:
            print(f"未找到预期的按钮文案，当前职位可能已经投递过，当前按钮文本: '{button_text}'")
            return False
            
    except Exception as apply_error:
        print(f"尝试投递职位 '{job_name}' 时出错: {str(apply_error)}")
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
        process_job_listings(driver, max_jobs=200)

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
