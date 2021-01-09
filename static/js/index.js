$(document).ready(function(){
    var x = document.getElementById("hi_im_tired");

    $(function() {
        $('#check_button').on('click', function(e) {
            e.preventDefault()
            var y = document.getElementById("check_button")
            // if(y.innerHTML === "Check"){
            y.innerHTML = '<span class="spinner-border spinner-border-sm" id="check_spinner" role="status"></span> Looking...'
            // }
            $.getJSON('/check_visible/',
                function(data) {
                    // console.log("jq here")
                    status = data
                    // hide load icon when found and show check
                    if(status == "found"){
                        y.innerHTML = "Found!"
                    }
                    else{
                        y.innerHTML = "Not found..."
                    }
            });
        });
    });

    // var form = document.getElementById("post_form");
    var btn = document.getElementById("track_button");
    btn.addEventListener("click", function () {
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" id="check_spinner" role="status"></span> Tracking...'
    });

    // $('#toggle_instr_btn').click(function () {
    //     // var z = $('#toggle_instr_btn')
    //     // var x = $('#instr')
    //     var z = document.getElementById("toggle_instr_btn");
    //     if(z.innerHTML === 'Show'){
    //         z.innerHTML = 'Hide';
    //         // console.log(x.innerHTML)
    //         x.innerHTML=''
    //         // x.display.style="block"
    //     }
    //     else{
    //         z.innerHTML = 'Show';
    //         x.innerHTML=''
    //         // x.display.style="none";
    //     }
    // });
});

