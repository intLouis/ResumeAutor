from transformers import AutoTokenizer, AutoModelForMaskedLM, pipeline
import jieba

# # 加载分词器
# tokenizer = AutoTokenizer.from_pretrained('papluca/xlm-roberta-base-language-detection')
#
# # 测试文本（包含中英文）
# text = """
# 你想尝试其他分词器吗？或者有什么特定的分词需求？
# """
#
#
# # 2. 获取实际的token
# tokens = tokenizer.tokenize(text)
# print("\n2. Actual tokens:")
# print(tokens)
#

mixed_text = """
文本分词（Tokenization）
BERT采用WordPiece分词器对原始文本进行子词分割，解决未登录词（OOV）问题，其流程包括：

BasicTokenizer：初步分词，处理空格分割、标点符号、中文字符等（如将中文按字符切分）5。

WordpieceTokenizer：在初步分词基础上，通过贪婪最长匹配算法（greedy longest-match-first）将词进一步拆分为子词（subword），例如将"repairing"拆分为"repair"和"##ing"58。

特殊标记插入：在文本首尾添加[CLS]（分类标记）和[SEP]（分隔标记），多句输入时用[SEP]分隔8。
"""



print("\n==== 中英文混合文本处理示例 ====")

# 1. XLM-RoBERTa - 优秀的多语言模型
print("\n1. 使用XLM-RoBERTa处理中英文混合文本:")
xlm_tokenizer = AutoTokenizer.from_pretrained("FacebookAI/xlm-roberta-base")
xlm_tokens = xlm_tokenizer.tokenize(mixed_text)
print("XLM-RoBERTa 分词结果:", xlm_tokens)

# 2. mBERT - 多语言BERT
print("\n2. 使用mBERT处理中英文混合文本:")
mbert_tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
mbert_tokens = mbert_tokenizer.tokenize(mixed_text)
print("mBERT 分词结果:", mbert_tokens)

# 3. 自定义jieba+transformers方法
print("\n3. 使用jieba+transformers处理中英文混合文本:")
def custom_tokenize(text):
    words = jieba.lcut(text)
    final_tokens = []
    for word in words:
        # 检测是否包含中文字符
        if any('\u4e00' <= char <= '\u9fff' for char in word):
            final_tokens.append(word)
        else:
            # 对英文使用XLM-RoBERTa进行次级分词
            subwords = xlm_tokenizer.tokenize(word)
            final_tokens.extend(subwords)
    return final_tokens

custom_tokens = custom_tokenize(mixed_text)
print("自定义方法分词结果:", custom_tokens)

# 4. 基于XLM-RoBERTa的掩码预测示例
print("\n4. 掩码预测示例 (使用XLM-RoBERTa):")
try:
    masked_text = "AI技术正在迅速<mask>，GPT和BERT都是优秀的语言模型。"
    fill_mask = pipeline("fill-mask", model="xlm-roberta-base")
    result = fill_mask(masked_text.replace("<mask>", fill_mask.tokenizer.mask_token))
    for r in result[:3]:  # 显示前3个预测结果
        print(f"预测: '{r['token_str']}', 分数: {r['score']:.4f}")
except Exception as e:
    print(f"掩码预测尝试失败: {e}")
    print("注意: 请确保已安装必要的依赖，如torch等")

print("\n推荐用于中英文混合任务的模型:")
print("1. XLM-RoBERTa - 优秀的多语言模型，支持100+语言")
print("2. mBERT - 多语言BERT，支持104种语言")
print("3. InfoXLM/XLM-E - 微软开发的多语言模型")
print("4. ERNIE - 百度开发，对中文理解较好")
print("5. Chinese-BERT-wwm - 采用全词掩码，对中文词汇理解更好")