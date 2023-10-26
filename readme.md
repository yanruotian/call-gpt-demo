# 调用OpenAI接口脚本

## 运行环境

- `python3.8`及以上。
- 需要安装 `openai`、`requests`库。

## 运行方式

本仓库由两部分组成：`src`模块和 `run-all.py`示例脚本，两者均可用于运行。

### 运行 `src`模块

在与 `src`文件夹同级的目录，在终端中运行：

```bash
python3 -m src
```

会打开交互式窗口：

```
Welcome to chatgpt prompt.
To exit, type ".exit".
>
```

直接输入想向GPT提交的问题即可。可以用 `.line`和 `.end`标签包裹多行内容。

若要从中退出，可以输入 `.exit`。

**注**：直接运行 `src`模块时，`api-key`通过 `src/main.py`的 `get_api_key`返回。当前预设的几个 `api-key`似乎均已经失效。

### 运行 `run-all.py`脚本

该脚本实际上是调用了 `src`中实现的一些接口。

如果需要进行情感判断的文件被放置于 `input_dir`，希望将结果输出于 `output_dir`，可以如下调用：

```bash
python3 run-all.py -i input_dir -o output_dir
```

其中 `-o`选项可以省略，默认值为 `<input_dir>-result`。

#### 数据格式要求

仓库中已在 `test-data`提供了一份样例数据文件夹，其中数据应该以 `jsonl`文件的形式存储于其中，每一行需要有 `rawContent`和 `keyword`字段。

#### 更改调用接口

当前 `run-all.py`默认使用轮询式调用OpenAI的GPT3.5的接口（`from src.fast_pool import askOne`）。如要调用清华GPT4接口应改为 `from src.main import askOne4 as askOne`。

#### 增加 `api-key`

轮询式接口调用的 `api-key`列表储存于 `/src/api-keys`下的 `txt`文件中，每一行以 ` : `（注意冒号前后有空格）分隔，左边是账号信息（这部分无用），右边是 `api-key`。需要增加 `api-key`则在 `txt`文件追加或者新建额外的 `txt`文件即可。

### 设置合适的`PROMPT`

每个`askOne`接口都有传入`PROMPT`的参数，按需修改即可。`temperature`同理。
