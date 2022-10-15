let input_message = $("#input-message");
let message_body = $(".msg_card_body");
let send_message_form = $("#send-message-form");
var USER_ID = $("#logged-in-user").val();

let loc = window.location;
let wsStart = "ws://";

if (loc.protocol === "https") {
  wsStart = "wss://";
}
let endpoint = wsStart + loc.host + loc.pathname;

var socket = new WebSocket(endpoint);

socket.onopen = async function (e) {
  console.log("open", e);
  send_message_form.on("submit", function (e) {
    e.preventDefault();
    let message = input_message.val();
    let send_to = get_active_other_user_id();
    let thread_id = get_active_thread_id();
    // if (USER_ID == 1) send_to = 2;
    // else send_to = 1;
    let data = {
      message: message,
      sent_by: USER_ID,
      send_to: send_to,
      thread_id: thread_id,
    };
    data = JSON.stringify(data);
    socket.send(data);
    $(this)[0].reset();
  });
};

socket.onmessage = async function (e) {
  console.log("message", e);
  let data = JSON.parse(e.data);
  let message = data["message"];
  let sent_by_id = data["sent_by"];
  newMessage(message, sent_by_id);
};

socket.onerror = async function (e) {
  console.log("error", e);
};

socket.onclose = async function (e) {
  console.log("close", e);
};

function newMessage(message, sent_by_id) {
  if ($.trim(message) === "") {
    return false;
  }
  let message_element;
  if (sent_by_id == USER_ID) {
    message_element = `
			<div class="d-flex mb-4 replied">
				<div class="msg_cotainer_send">
					${message}
					
				</div>
				<div class="img_cont_msg">
					<img src="../img/avatar.jpg" class="rounded-circle user_img_msg">
				</div>
			</div>
	    `;
  } else {
    message_element = `
			<div class="d-flex mb-4 received">
            <div class="img_cont_msg">
					<img src="../img/avatar.jpg" class="rounded-circle user_img_msg">
				</div>
				<div class="msg_cotainer">
					${message}
					
				</div>
				
			</div>
	    `;
  }

  message_body.append($(message_element));
  message_body.animate(
    {
      screenTop: $(document).height(),
    },
    100
  );
  input_message.val(null);
}

//not working
$(".contact-li").on("click", function () {
  $(".contacts .active").removeClass("active");
  $(this).addClass("active");

  // message wrappers
  let chat_id = $(this).attr("chat-id");
  $(".messages-wrapper.is_active").removeClass("is_active");
  $('.messages-wrapper[chat-id="' + chat_id + '"]').addClass("is_active");
});

function get_active_other_user_id() {
  let other_user_id = $(".messages-wrapper.is_active").attr("other-user-id");
  other_user_id = $.trim(other_user_id);
  return other_user_id;
}

function get_active_thread_id() {
  let thread_id = $("#thread-id").val();
  return thread_id;
}
