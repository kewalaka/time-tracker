var activeTask = null;

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
  $.ajax({
    url: 'http://127.0.0.1:5000/tasks/' + taskName + '/time',
    type: 'PUT',
    contentType: 'application/json',
    data: JSON.stringify({ time: Date.now() })
  });
});

// Switch to task
function switchTask(taskName) {
  if (activeTask !== null) {
    $('.task-item').removeClass('active');
    clearInterval(intervalId);
    $.ajax({
      url: 'http://127.0.0.1:5000/tasks/' + activeTask + '/stop',
      type: 'POST'
    });
  }
  activeTask = taskName;
  $('.task-item:contains(' + taskName + ')').addClass('active');
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