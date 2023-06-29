var activeTask = null;
var intervalId = null;

$(function () {
  // Get tasks from backend
  $.ajax({
    url: 'http://127.0.0.1:5000/tasks',
    type: 'GET',
    success: function (data) {
      // Populate task list
      var taskList = $('#task-list');
      for (var taskName in data) {
        var taskItem = $('<div class="task-item">')
          .text(taskName)
          .click(function () {
            switchTask($(this).text());
          });
        if (data[taskName].active) {
          taskItem.addClass('active');
        }
        taskList.append(taskItem);
      }
    }
  });
});

// Create new task
$('#new-task-form').submit(function (event) {
  event.preventDefault();
  var taskName = $('#task-name').val();
  if (taskName === '') {
    return;
  }
  $.ajax({
    url: 'http://127.0.0.1:5000/tasks',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ name: taskName }),
    success: function (data) {
      // Add task to list
      var taskItem = $('<div class="task-item">')
        .text(data.name)
        .click(function () {
          switchTask(data.name);
        });
      $('#task-list').append(taskItem);
    }
  });
  $('#task-name').val('');
});

// Click event handler for task items
$('.task-item').click(function () {
  var taskName = $(this).text();
  $('.task-item').removeClass('active');
  $(this).addClass('active');
  clearInterval(intervalId);
  $.ajax({
    url: 'http://127.0.0.1:5000/tasks/' + taskName + '/start',
    type: 'POST'
  });
  activeTask = taskName;
  var startTime = Date.now();
  intervalId = setInterval(function () {
    var elapsedTime = Date.now() - startTime;
    var hours = Math.floor(elapsedTime / 3600000);
    var minutes = Math.floor((elapsedTime % 3600000) / 60000);
    var timeString = hours + 'h ' + minutes + 'm';
    $('.task-item.active').find('.task-time').text(timeString);
  }, 60000);
});

// Switch to task
function switchTask(taskName) {
  if (activeTask !== null) {
    clearInterval(intervalId);
    $.ajax({
      url: 'http://127.0.0.1:5000/tasks/' + activeTask + '/stop',
      type: 'POST'
    });
  }
  activeTask = taskName;
  $('.task-item').removeClass('active');
  $('.task-item').filter(function () {
    return $(this).text() === taskName;
  }).addClass('active');
  var startTime = Date.now();
  intervalId = setInterval(function () {
    var elapsedTime = Date.now() - startTime;
    var hours = Math.floor(elapsedTime / 3600000);
    var minutes = Math.floor((elapsedTime % 3600000) / 60000);
    var timeString = hours + 'h ' + minutes + 'm';
    $('.task-item.active').find('.task-time').text(timeString);
  }, 60000);
  $.ajax({
    url: 'http://127.0.0.1:5000/tasks/' + taskName + '/start',
    type: 'POST'
  });
}

// Delete task
$('#delete-task').click(function () {
  if (activeTask !== null) {
    $('.task-item:contains(' + activeTask + ')').remove();
    $.ajax({
      url: 'http://127.0.0.1:5000/tasks/' + activeTask,
      type: 'DELETE'
    });
    activeTask = null;
  }
});