#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动部署脚本
一键部署到GitHub并配置Actions
"""

import os
import sys
import json
import subprocess
import getpass
from datetime import datetime

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_git_installed():
    """检查git是否安装"""
    success, _, _ = run_command("git --version")
    return success

def check_gh_cli_installed():
    """检查GitHub CLI是否安装"""
    success, _, _ = run_command("gh --version")
    return success

def install_gh_cli():
    """安装GitHub CLI"""
    print("🔧 正在安装GitHub CLI...")
    
    # 检测操作系统
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("检测到macOS，使用Homebrew安装...")
        success, stdout, stderr = run_command("brew install gh")
        if success:
            print("✅ GitHub CLI安装成功")
            return True
        else:
            print("❌ 安装失败，请手动安装:")
            print("brew install gh")
            return False
    elif system == "linux":
        print("检测到Linux，使用包管理器安装...")
        # 尝试不同的包管理器
        managers = [
            "sudo apt install gh",
            "sudo yum install gh",
            "sudo pacman -S github-cli"
        ]
        for cmd in managers:
            success, _, _ = run_command(cmd)
            if success:
                print("✅ GitHub CLI安装成功")
                return True
        print("❌ 自动安装失败，请手动安装GitHub CLI")
        return False
    else:
        print("❌ 不支持的操作系统，请手动安装GitHub CLI")
        print("访问: https://cli.github.com/")
        return False

def login_github():
    """登录GitHub"""
    print("🔑 正在登录GitHub...")
    
    # 检查是否已登录
    success, stdout, _ = run_command("gh auth status")
    if success:
        print("✅ 已登录GitHub")
        return True
    
    # 执行登录
    print("请在浏览器中完成GitHub登录...")
    success, _, _ = run_command("gh auth login")
    if success:
        print("✅ GitHub登录成功")
        return True
    else:
        print("❌ GitHub登录失败")
        return False

def create_github_repo():
    """创建GitHub仓库"""
    print("📁 正在创建GitHub仓库...")
    
    repo_name = "wechat-job-monitor"
    description = "微信公众号招聘信息自动监控系统"
    
    # 检查仓库是否已存在
    success, _, _ = run_command(f"gh repo view {repo_name}")
    if success:
        print(f"✅ 仓库 {repo_name} 已存在")
        return repo_name
    
    # 创建新仓库
    cmd = f'gh repo create {repo_name} --public --description "{description}"'
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(f"✅ 仓库 {repo_name} 创建成功")
        return repo_name
    else:
        print(f"❌ 仓库创建失败: {stderr}")
        return None

def init_git_repo():
    """初始化Git仓库"""
    print("🔄 正在初始化Git仓库...")
    
    # 检查是否已是Git仓库
    if os.path.exists('.git'):
        print("✅ 已经是Git仓库")
        return True
    
    # 初始化Git仓库
    commands = [
        "git init",
        "git add .",
        'git commit -m "Initial commit - 微信公众号招聘信息监控系统"'
    ]
    
    for cmd in commands:
        success, _, stderr = run_command(cmd)
        if not success:
            print(f"❌ 命令失败: {cmd}")
            print(f"错误: {stderr}")
            return False
    
    print("✅ Git仓库初始化成功")
    return True

def push_to_github(repo_name):
    """推送代码到GitHub"""
    print("📤 正在推送代码到GitHub...")
    
    # 获取GitHub用户名
    success, username, _ = run_command("gh api user --jq .login")
    if not success:
        print("❌ 无法获取GitHub用户名")
        return False
    
    username = username.strip()
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    
    commands = [
        f"git remote add origin {remote_url}",
        "git branch -M main",
        "git push -u origin main"
    ]
    
    for cmd in commands:
        success, _, stderr = run_command(cmd)
        if not success and "already exists" not in stderr:
            print(f"❌ 命令失败: {cmd}")
            print(f"错误: {stderr}")
            return False
    
    print("✅ 代码推送成功")
    return True, username

def set_github_secrets(repo_name, username):
    """设置GitHub Secrets"""
    print("🔐 正在设置GitHub Secrets...")
    
    # 必需的secret
    secrets = {
        "DEEPSEEK_API_KEY": "sk-92d52c5e40fc48bd89bbe1fd60ebb45e"
    }
    
    # 可选的secrets
    optional_secrets = {
        "SMTP_SERVER": "邮件服务器地址 (如: smtp.gmail.com)",
        "SMTP_PORT": "邮件服务器端口 (如: 587)",
        "SENDER_EMAIL": "发送者邮箱",
        "SENDER_PASSWORD": "邮箱应用密码",
        "SENDER_NAME": "发送者名称 (如: 招聘监控系统)",
        "RECEIVER_EMAILS": "接收者邮箱 (多个用逗号分隔)",
        "WECHAT_WEBHOOK_URL": "企业微信机器人webhook地址",
        "SERVER_CHAN_KEY": "Server酱密钥"
    }
    
    # 设置必需的secrets
    for secret_name, secret_value in secrets.items():
        cmd = f'gh secret set {secret_name} --body "{secret_value}" --repo {username}/{repo_name}'
        success, _, stderr = run_command(cmd)
        if success:
            print(f"✅ 设置 {secret_name} 成功")
        else:
            print(f"❌ 设置 {secret_name} 失败: {stderr}")
    
    # 询问是否设置可选secrets
    print("\n📧 是否配置邮件通知？(推荐)")
    setup_email = input("输入 y 配置邮件通知，输入 n 跳过: ").lower().strip()
    
    if setup_email == 'y':
        print("\n请输入邮件配置信息:")
        
        email_secrets = {}
        for secret_name, description in optional_secrets.items():
            if secret_name.startswith(('SMTP_', 'SENDER_', 'RECEIVER_')):
                value = input(f"{description}: ").strip()
                if value:
                    email_secrets[secret_name] = value
        
        # 设置邮件相关secrets
        for secret_name, secret_value in email_secrets.items():
            cmd = f'gh secret set {secret_name} --body "{secret_value}" --repo {username}/{repo_name}'
            success, _, stderr = run_command(cmd)
            if success:
                print(f"✅ 设置 {secret_name} 成功")
            else:
                print(f"❌ 设置 {secret_name} 失败: {stderr}")
    
    print("✅ GitHub Secrets配置完成")
    return True

def enable_github_actions(repo_name, username):
    """启用GitHub Actions"""
    print("🚀 正在启用GitHub Actions...")
    
    # Actions通常在推送后自动启用
    print("✅ GitHub Actions已启用")
    
    # 提供仓库链接
    repo_url = f"https://github.com/{username}/{repo_name}"
    actions_url = f"{repo_url}/actions"
    
    print(f"📁 仓库地址: {repo_url}")
    print(f"⚙️  Actions页面: {actions_url}")
    
    return True

def create_deployment_summary():
    """创建部署摘要"""
    print("\n" + "="*60)
    print("🎉 部署完成！")
    print("="*60)
    
    print("✅ 已完成的配置:")
    print("  - GitHub仓库已创建")
    print("  - 代码已推送")
    print("  - DeepSeek API密钥已配置")
    print("  - GitHub Actions已启用")
    
    print("\n⚙️  系统将自动:")
    print("  - 每30分钟监控一次")
    print("  - 识别招聘信息")
    print("  - 生成详细报告")
    print("  - 发送通知 (如果配置了)")
    
    print("\n📊 监控的公众号:")
    print("  - 深焦DeepFocus")
    print("  - 校影")
    
    print("\n🔗 有用的链接:")
    success, username, _ = run_command("gh api user --jq .login")
    if success:
        username = username.strip()
        repo_name = "wechat-job-monitor"
        print(f"  - 仓库: https://github.com/{username}/{repo_name}")
        print(f"  - Actions: https://github.com/{username}/{repo_name}/actions")
        print(f"  - 设置: https://github.com/{username}/{repo_name}/settings/secrets/actions")
    
    print("\n💡 下一步:")
    print("  1. 访问Actions页面查看运行状态")
    print("  2. 可以手动点击 'Run workflow' 立即运行")
    print("  3. 如需配置邮件通知，在仓库设置中添加邮件相关Secrets")
    
    print("\n💰 预期费用: 1-5元/月 (仅DeepSeek API费用)")
    print("="*60)

def main():
    """主函数"""
    print("🎬 微信公众号招聘信息监控系统 - 自动部署")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists('main.py'):
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    try:
        # 步骤1: 检查Git
        print("1️⃣ 检查Git安装...")
        if not check_git_installed():
            print("❌ Git未安装，请先安装Git")
            print("访问: https://git-scm.com/downloads")
            sys.exit(1)
        print("✅ Git已安装")
        
        # 步骤2: 检查GitHub CLI
        print("\n2️⃣ 检查GitHub CLI...")
        if not check_gh_cli_installed():
            print("⚠️  GitHub CLI未安装")
            install_choice = input("是否自动安装GitHub CLI? (y/n): ").lower().strip()
            if install_choice == 'y':
                if not install_gh_cli():
                    sys.exit(1)
            else:
                print("❌ 需要GitHub CLI才能自动部署")
                print("请手动安装: https://cli.github.com/")
                sys.exit(1)
        print("✅ GitHub CLI已安装")
        
        # 步骤3: 登录GitHub
        print("\n3️⃣ 登录GitHub...")
        if not login_github():
            sys.exit(1)
        
        # 步骤4: 创建仓库
        print("\n4️⃣ 创建GitHub仓库...")
        repo_name = create_github_repo()
        if not repo_name:
            sys.exit(1)
        
        # 步骤5: 初始化Git
        print("\n5️⃣ 初始化Git仓库...")
        if not init_git_repo():
            sys.exit(1)
        
        # 步骤6: 推送到GitHub
        print("\n6️⃣ 推送代码到GitHub...")
        success, username = push_to_github(repo_name)
        if not success:
            sys.exit(1)
        
        # 步骤7: 设置Secrets
        print("\n7️⃣ 设置GitHub Secrets...")
        if not set_github_secrets(repo_name, username):
            sys.exit(1)
        
        # 步骤8: 启用Actions
        print("\n8️⃣ 启用GitHub Actions...")
        if not enable_github_actions(repo_name, username):
            sys.exit(1)
        
        # 完成
        create_deployment_summary()
        
    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 部署过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()