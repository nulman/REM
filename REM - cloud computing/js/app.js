var app = angular.module('store', [ ]);

var url = "localhost:5000"

// //requesting the tree explorer - first call
// $.ajax({
//   type: "POST",
//   url: url,
//   data: "getInitialTree",
//   success: drawInitialTree,
//   dataType: json
// });

// function drawInitialTree(data){
//   $('#jstree').jstree(data);
// }

// //on click event on folder in tree - request folder data
// $('#jstree').on("changed.jstree", function (e, data) {
//   console.log(data.selected);
// });

// $('#mytree').jstree(true).settings.core.data = new_data;
// $('#mytree').jstree(true).redraw(true);




// //creating the tree explorer
// var treeJson = { 'core' : {
// 		"themes": {
//                 "name": "default-dark",
//                 "dots": true,
//                 "icons": true
//             },
//     'data' : [
//        'Root node 1',
//        {
//          'text' : 'Root node 2',
//          'state' : {
//            'opened' : true,
//            'selected' : true
//          },
//          'children' : [
//            { 'text' : 'Child 1' , 'icon' : 'glyphicon glyphicon-file'},
//            {'text':'Child 2', 'icon':'glyphicon glyphicon-file'}
//          ]
//       }
//     ]} 
// };

// $(function () { $('#jstree').jstree(treeJson); 
// });

treeScript();

$('#jstree').on("changed.jstree", function (e, data) {
  console.log(data.selected);
});

$('button').on('click', function () {
  $('#jstree').jstree(true).select_node('child_node_1');
  $('#jstree').jstree('select_node', 'child_node_1');
  $.jstree.reference('#jstree').select_node('child_node_1');
});

//display the correct div in create/load
//fill the parameters options in create section
$(document).ready(function() {
$("div.desc").hide();
$("input[name$='work-type']").click(function() {
        var type = $(this).val();

        $("div.desc").hide();
        $("#"+ type + "-selection").show();

        if(type=="create"){
        	var json = ["anon_pages", "cache_and_buff", "cpu_0", "cpu_1", "cpu_10", "cpu_11", "cpu_12", "cpu_13", "cpu_14", "cpu_15", "cpu_16", "cpu_17", "cpu_18", "cpu_19", "cpu_2", "cpu_20", "cpu_21", "cpu_22", "cpu_23", "cpu_3", "cpu_4", "cpu_5", "cpu_6", "cpu_7", "cpu_8", "cpu_9", "cpu_tot", "cpu_usage", "duration", "host_major_faults", "host_minor_faults", "io_percent", "io_percent_0", "io_percent_1", "io_percent_10", "io_percent_11", "io_percent_12", "io_percent_13", "io_percent_14", "io_percent_15", "io_percent_16", "io_percent_17", "io_percent_18", "io_percent_19", "io_percent_2", "io_percent_20", "io_percent_21", "io_percent_22", "io_percent_23", "io_percent_3", "io_percent_4", "io_percent_5", "io_percent_6", "io_percent_7", "io_percent_8", "io_percent_9", "io_percent_tot", "load", "major_fault", "mem_available", "mem_free", "mem_unused", "minor_fault", "name", "perf-duration", "perf-number_of_clients", "perf-number_of_threads", "perf-query01_latency", "perf-query02_latency", "perf-query03_latency", "perf-query04_latency", "perf-query05_latency", "perf-query06_latency", "perf-query07_latency", "perf-query08_latency", "perf-query09_latency", "perf-query10_latency", "perf-query11_latency", "perf-query12_latency", "perf-query13_latency", "perf-query14_latency", "perf-query_mode", "perf-scaling_factor", "perf-tps_with_connections_time", "perf-tps_without_connections_time", "perf-transactions_count", "prog", "python1_usage", "python2_usage", "rss", "running_time", "swap_in", "swap_out", "time", "type"];
        	$.each(json, function(i, value) {
            	$('#x-axis').append($('<option>').text(value).attr('value', value));
            	$('#y-axis').append($('<option>').text(value).attr('value', value));
        	});
        }
    });

//display final graph
$("#generate-graph").attr("src","figure.html");

});

///////////////////////////
function treeScript(){

    $(function() {
      //var url = 'https://www.jstree.com/demo_filebrowser/index.php?operation=get_node';  
      var url = "192.168.1.101:5000/listdir"
      $('#jstree')
        .jstree({
          'core' : {
            'data' : {
              'url' : url,
              'data' : function (node) {
                return { 'id' : node.id };
              }
            },
            'check_callback' : function(o, n, p, i, m) {
              if(m && m.dnd && m.pos !== 'i') { return false; }
              if(o === "move_node" || o === "copy_node") {
                if(this.get_node(n).parent === this.get_node(p).id) { return false; }
              }
              return true;
            },
            'themes' : {
              'responsive' : true,
              'variant' : 'small',
              'stripes' : true
            }
          },
          'sort' : function(a, b) {
            return this.get_type(a) === this.get_type(b) ? (this.get_text(a) > this.get_text(b) ? 1 : -1) : (this.get_type(a) >= this.get_type(b) ? 1 : -1);
          },
          // 'contextmenu' : {
          //   'items' : function(node) {
          //     var tmp = $.jstree.defaults.contextmenu.items();
          //     delete tmp.create.action;
          //     tmp.create.label = "New";
          //     tmp.create.submenu = {
          //       "create_folder" : {
          //         "separator_after" : true,
          //         "label"       : "Folder",
          //         "action"      : function (data) {
          //           var inst = $.jstree.reference(data.reference),
          //             obj = inst.get_node(data.reference);
          //           inst.create_node(obj, { type : "default" }, "last", function (new_node) {
          //             setTimeout(function () { inst.edit(new_node); },0);
          //           });
          //         }
          //       },
          //       "create_file" : {
          //         "label"       : "File",
          //         "action"      : function (data) {
          //           var inst = $.jstree.reference(data.reference),
          //             obj = inst.get_node(data.reference);
          //           inst.create_node(obj, { type : "file" }, "last", function (new_node) {
          //             setTimeout(function () { inst.edit(new_node); },0);
          //           });
          //         }
          //       }
          //     };
          //     if(this.get_type(node) === "file") {
          //       delete tmp.create;
          //     }
          //     return tmp;
          //   }
          // },
          'types' : {
            'default' : { 'icon' : 'folder' },
            'file' : { 'valid_children' : [], 'icon' : 'file' }
          },
          'unique' : {
            'duplicate' : function (name, counter) {
              return name + ' ' + counter;
            }
          },
          'plugins' : ['state','dnd','sort','types','contextmenu','unique']
        })
        // .on('delete_node.jstree', function (e, data) {
        //   $.get('?operation=delete_node', { 'id' : data.node.id })
        //     .fail(function () {
        //       data.instance.refresh();
        //     });
        // })
        // .on('create_node.jstree', function (e, data) {
        //   $.get('?operation=create_node', { 'type' : data.node.type, 'id' : data.node.parent, 'text' : data.node.text })
        //     .done(function (d) {
        //       data.instance.set_id(data.node, d.id);
        //     })
        //     .fail(function () {
        //       data.instance.refresh();
        //     });
        // })
        // .on('rename_node.jstree', function (e, data) {
        //   $.get('?operation=rename_node', { 'id' : data.node.id, 'text' : data.text })
        //     .done(function (d) {
        //       data.instance.set_id(data.node, d.id);
        //     })
        //     .fail(function () {
        //       data.instance.refresh();
        //     });
        // })
        // .on('move_node.jstree', function (e, data) {
        //   $.get('?operation=move_node', { 'id' : data.node.id, 'parent' : data.parent })
        //     .done(function (d) {
        //       //data.instance.load_node(data.parent);
        //       data.instance.refresh();
        //     })
        //     .fail(function () {
        //       data.instance.refresh();
        //     });
        // })
        // .on('copy_node.jstree', function (e, data) {
        //   $.get('?operation=copy_node', { 'id' : data.original.id, 'parent' : data.parent })
        //     .done(function (d) {
        //       //data.instance.load_node(data.parent);
        //       data.instance.refresh();
        //     })
        //     .fail(function () {
        //       data.instance.refresh();
        //     });
        // })
        // .on('changed.jstree', function (e, data) {
        //   if(data && data.selected && data.selected.length) {
        //     $.get('?operation=get_content&id=' + data.selected.join(':'), function (d) {
        //       if(d && typeof d.type !== 'undefined') {
        //         $('#data .content').hide();
        //         switch(d.type) {
        //           case 'text':
        //           case 'txt':
        //           case 'md':
        //           case 'htaccess':
        //           case 'log':
        //           case 'sql':
        //           case 'php':
        //           case 'js':
        //           case 'json':
        //           case 'css':
        //           case 'html':
        //             $('#data .code').show();
        //             $('#code').val(d.content);
        //             break;
        //           case 'png':
        //           case 'jpg':
        //           case 'jpeg':
        //           case 'bmp':
        //           case 'gif':
        //             $('#data .image img').one('load', function () { $(this).css({'marginTop':'-' + $(this).height()/2 + 'px','marginLeft':'-' + $(this).width()/2 + 'px'}); }).attr('src',d.content);
        //             $('#data .image').show();
        //             break;
        //           default:
        //             $('#data .default').html(d.content).show();
        //             break;
        //         }
        //       }
        //     });
        //   }
        //   else {
        //     $('#data .content').hide();
        //     $('#data .default').html('Select a file from the tree.').show();
        //   }
        // });
      });
}