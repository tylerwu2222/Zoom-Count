// delete row corresponding to button clicked
function deleteRow(btn){
    var row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

// adds row to class table
function addRow(){
    // rowCount++; // using rowCount for id
    var row = $("<tr>");
    row.append($('<td><input name="classNames[]" type="text" placeholder="Class Name" required/></td>'))
        .append($('<td><input name="classSizes[]" type="number" value="100" step="1" required/></td>'))
        .append($('<td><input name="startTimes[]" type="time" value="10:00" id="start_time" step=300 required></td>'))
        .append($('<td><input name="endTimes[]" type="time" value="11:00" id="end_time" step=300 required></td>'))
        .append($('<td><input name="classLengths[]" type="number" id="class_length" value="1" min="0.25" max="10" step="0.25" required></td>'))
        .append($('<td><input name="subjects[]" type="text" placeholder="Subject"/></td>'))
        .append($('<td><input name="PERs[]" type="number" value="6" min="1" max="10" step="1"/></td>'))
        .append($(`<td><button type="button" class="close" aria-label="Close" style="border:none; background:none; color:rgb(255, 0, 76); font-weight:bold;" onclick="deleteRow(this)"><span aria-hidden="true">&times;</span></button></td>`));
 
  $("#class_tbl tbody").append(row);
}

