function getImgUrl(){
	id = [];
	id.push(1+Math.round(Math.random()*7));
	for(var i=0;i<5;i++)id.push(Math.round(Math.random()*9));
		return 'https://wallpapers.wallhaven.cc/wallpapers/thumb/small/th-747189.jpg'
	return 'https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-738724.jpg';
	return 'https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-'+id.join('')+'.jpg';
}
var surl = getImgUrl();

var app = new Vue({
	el:'#container',
	data:{
		fileChoosed:false,
		sentence:"Please upload an image first",
		sentence_ch:"请上传图片先",

		isCropping:false,
		isSubmitting:false,
		imgurl:surl,
		loading: false,

		cropBtnText:"Crop",
		cropper:null,
	},
	methods:{
		showPreview:function(fileId, imgId) {
			var file = document.getElementById('inputbox');
			if(!file.value)return;
			var ua = navigator.userAgent.toLowerCase();
			var url = '';
			if(/msie/.test(ua)) {
				url = file.value;
			} else {
				url = window.URL.createObjectURL(file.files[0]);
			}
			this.convertImgToBase64(url,function(base64URL){
				app.imgurl = base64URL;
				app.fileChoosed = true;
			});
		},
		getres:function(event){
			if(!this.fileChoosed){
				this.$alert('点击如上图片选择您自己的图片呀', '呀！', {
					confirmButtonText: '明白了',
					callback: action => {
						// this.$message({
						// 	type: 'info',
						// 	message: `action: ${ action }`
						// });
					}
				});
				return;
			}
			this.isSubmitting = true;
			let formData = new FormData();
			formData.append('imgbase64',this.imgurl);
			let config = {
				headers: {
					'Content-Type': 'multipart/form-data'
				}
			}
			this.loading = true;
			axios.post('/api',formData,config)
			.then((response)=>{
				f = response;
				this.sentence = response.data.sentence;  
				this.sentence_ch = response.data.sentence_ch;
				this.$notify({
					title: 'English',
					message: response.data.sentence,
					duration: 4000,
					position: 'bottom-left'
				});
				this.$notify({
					title: '中文',
					message: response.data.sentence_ch,
					duration: 4000
				});
				this.loading = false;
				this.isSubmitting = false;
			})
			.catch((error)=>{
				console.log(error);
			});
		},
		crop:function(){
			if(this.cropper==null){ //Crop
				this.isCropping = true;
				this.cropper = new Cropper(document.getElementById('userimg'), {
					aspectRatio: 1 / 1
				});
				const loading = this.$loading({
					lock: true,
					text: '正在拼命启动裁剪模式',
					spinner: 'el-icon-loading',
					background: 'rgba(0, 0, 0, 0.7)'
				});
				setTimeout(() => {
					loading.close();
					this.cropBtnText = "OK";
				}, 3500);
			}else{  //OK
				this.imgurl = this.cropper.getCroppedCanvas().toDataURL('image/png')
				const loading = this.$loading({
					lock: true,
					text: '完成裁剪,关闭裁剪模式中',
					spinner: 'el-icon-loading',
					background: 'rgba(0, 0, 0, 0.7)'
				});
				setTimeout(() => {
					this.cropper.destroy();
					this.cropper = null;
					loading.close();
					this.cropBtnText = "Crop";
					this.isCropping = false;
				}, 1500);
			}
		},
		resetCrop:function(){
			if (this.cropper==null) {return}
			this.cropper.reset();
		},
		leftR:function(){
			if (this.cropper==null) {return}
			this.cropper.rotate(2);
		},
		rightR:function(){
			if (this.cropper==null) {return}
			this.cropper.rotate(-2);
		},
		convertImgToBase64:function(url, callback){
            var canvas = document.createElement('CANVAS'),
                    ctx = canvas.getContext('2d'),
                    img = new Image;
            img.crossOrigin = 'Anonymous';
            img.onload = function(){
                canvas.height = img.height;
                canvas.width = img.width;
                ctx.drawImage(img,0,0);
                var dataURL = canvas.toDataURL('image/png');
                callback.call(this, dataURL);
                canvas = null;
            };
            img.src = url;
        }
	}
});

