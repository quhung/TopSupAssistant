该项目是直接抄的 [TopSup](https://github.com/Skyexu/TopSup)和[MillionHeroAssistant](https://github.com/smileboywtu/MillionHeroAssistant)，感谢上面两位大佬。

上面两个项目都是用的 ocr，需要百度 key，而且有次数限制，比较麻烦，所以把上面两个项目的题目获取的方法改成用 xposed hook apk 的代码，然后发送一个请求到 Pc 上，然后再用上面两位大佬的程序搜索结果，耗时比较短

对应的android 项目[QAOnline](https://github.com/quhung/QAOnline),配合起来使用，pc拿到题目的时间大概在几十 ms 左右 ，比 ocr 快很多

