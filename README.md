# QQZone_Album_Upload
QQ相册自动上传照片

> 自动下载QQ空间相册可以看这个：https://github.com/1061700625/QQZone_AutoDownload_Album

---

粗糙版本。


**注意事项：**     
1. 使用前请先**解压Chrome.zip**，放到与**upload.py**同路径下。[Chrome.zip下载链接](https://raw.githubusercontent.com/1061700625/QQZone_AutoDownload_Album/master/Chrome.rar)

**脚本执行流程：**    
1. 自动打开浏览器，手动配合完成登录；
2. 将root_dir_path中的照片，按每个文件夹split_num张图进行拆分；
3. 将图片上传到username用户的album_url相册中。
4. 注意，QQ相册一次最多500张。    

**运行效果：**    
![image](https://user-images.githubusercontent.com/31002981/216118293-92600877-4ec5-4a84-b0da-569b87c68f1b.png)

**库：**
```bash
pip instal DrissionPage pyautoit pyautogui tqdm
```

