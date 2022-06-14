            $(document).ready(function () {
				var elem = document.getElementById('message')
				var max = Math.max(
				  document.body.scrollHeight, document.documentElement.scrollHeight,
				  document.body.offsetHeight, document.documentElement.offsetHeight,
				  document.body.clientHeight, document.documentElement.clientHeight
				);

				window.scrollTo(max, max);
				$('#sendmessage').hide()
            });

			window.onresize = function () {
				if(window.innerWidth <= 660){
				alert("Please make the screen bigger for a better experience!")
			}
			};
            function doThis() {
                jQuery.ajax({
                    url: window.location.href,
                    success: function (data) {
						if ($("#messages").html() == $(data).find("#messages").html()){
							
						}else{
                        $("#messages").html($(data).find("#messages").html());
						}
                    },
                    error: function (response) {
                        console.log(response);
                    },
                });
            }

			var textarea = document.getElementById('message')
			textarea.oninput = function() {
		    textarea.style.height = "";
			  	/* textarea.style.height = Math.min(textarea.scrollHeight, 300) + "px"; */
				var elem = document.getElementById('messagestuff')
				var max = Math.max(
				  document.body.scrollHeight, document.documentElement.scrollHeight,
				  document.body.offsetHeight, document.documentElement.offsetHeight,
				  document.body.clientHeight, document.documentElement.clientHeight
				);
				textarea.style.height = textarea.scrollHeight + "px"
				window.scrollTo(max, max);
			};
			
			function okop(event) {
                // 13 is the keycode for "enter"
                if (event.keyCode == 13 && event.shiftKey) {


                }
                if (event.keyCode == 13 && !event.shiftKey && $('#message').val().trim().length > 0) {
					event.preventDefault()
                    $('#messageform').submit()
                }
				if (event.keyCode == 13 && !event.shiftKey && $('#message').val().trim().length == 0) {
					event.preventDefault()
                }
            }
            setInterval(doThis, 2000);