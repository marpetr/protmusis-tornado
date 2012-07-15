REFRESH_INTERVAL = 1000;
SYNC_URL = '/sync';

currentView = '';
currentQID = 0;

Views = {
	idle: {
		show: function() { $('#idle_view').show(); },
		hide: function() { $('#idle_view').hide(); },
		update: function() {}
	},
	question: {
		show: function(data) {
			this.update(data);
			$('#question_view').show();
		},
		hide: function() {
			currentQID = 0;
			$('#question_view').hide();
		},
		update: function(data) {
			if (currentQID != data.qid) {
				if (!freeView)
					document.getElementById('question_textarea').value = data.cur_answer;
				document.getElementById('question_img').src = '/image?' + Math.random();
				$('#question_num').html(data.num);
				currentQID = data.qid;
			}
			$('#question_time_left').html(data.time_left);
		}
	}
}

function updateTeamView() {
	var params = {};
	if (!freeView && currentView == 'question') {
		params.currentQID = currentQID;
		params.currentText = document.getElementById('question_textarea').value;
	}
	var bg = new Date();
	$.post(SYNC_URL, params, function(data) {
		//var lag = ((new Date() - bg) / 1000).toFixed(3);
		//$('#debug').html(lag);
		if (currentView == data.view)
			Views[currentView].update(data);
		else {
			if (currentView)
				Views[currentView].hide(data);
			currentView = data.view;
			Views[currentView].show(data);
		}
		scheduleUpdate();
	});
}

function scheduleUpdate() {
	updateTimerID = setTimeout(updateTeamView, REFRESH_INTERVAL);
}

function initTeamView() {
	freeView = false;
	updateTeamView();
}

function initFreeView() {
	freeView = true;
	REFRESH_INTERVAL = 1000;
	SYNC_URL = '/free-view/state';
	updateTeamView();
}
