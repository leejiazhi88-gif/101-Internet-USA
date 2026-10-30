# 101 Internet USA 工作约定

本工作空间对应远端仓库：
`git@github.com:leejiazhi88-gif/101-Internet-USA.git`

飞书目标表：
https://my.feishu.cn/wiki/SWDBwMvwuiE5dzkex5rcFbs2n5f?sheet=K3baGL

## Git 同步

- 开始修改前运行 `git status` 和 `git fetch origin`，先检查远端是否有新提交。
- 保留用户已有未提交改动，不覆盖、不强推；有冲突时先说明并处理。
- 完成代码或说明修改后做必要验证，再提交到 `main` 并推送到 `origin/main`。
- Git 同步指代码、脚本、说明和配置约定的提交与推送，不代表后台自动刷新。
- 凭证、飞书令牌、飞书快照、行情缓存和临时输出只放本地，不提交。

## 本地数据

`work/` 下的 JSON、HTML、PDF、TXT、CSV、TSV 和缓存目录是本地运行产物，已在 `.gitignore` 中排除。Python 脚本仍会同步，便于后续迭代继续维护。

飞书 API 凭证通过环境变量或本地凭证文件提供，禁止写入代码或 Git。运行前确认 `FEISHU_APP_ID`、`FEISHU_APP_SECRET` 和 `FEISHU_WIKI_TOKEN` 已在本地配置。
