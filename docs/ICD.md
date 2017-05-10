<!--- Editor: Liran Funaro <funaro@cs.technion.ac.il> -->

# Listdir
Client creates the file explorer tree from the response.
Used when loading the page or when updating the file explorer upon user selection.

#### Parameters
String with the requested path or empty `[]`.

```javascript
"/media/pie/GIT/REM/server/experiments/exp1"
```

#### Response
A dictionary with 2 keys- json: which is used to generate the file explorer tree, and url: which provides the root directory url.

```javascript
{
    json: [,…],
    url: " /media/pie/GIT/REM/server/experiments/"
}
```

***

# getcolumns
Used when user clicks 'ok' on an experiment file, initiating the parameter generation

#### Parameters
String with the requested path (id of the selected node) or empty ```[]```.

```javascript
"/media/pie/GIT/REM/server/experiments/exp1"
```

#### Response
A dictionary with the column (cols) and the models of the specific experiment.

```javascript
{
    cols: ["arguments", "arguments-description", "avg",
           "cache-auction-round", "cache-auction-time",
           "cache-bid",…],
    models: {,…},
    Line: {
       x_axis: { type: "single", filterByValue: false },
       y_axis: { type: "single", filterByValue: false},
       …
    }
}
```

***

# Getvals
When a field is marked as 'filterByValue = true' we would like to filter by a specific value, and not by the column name.
When a user selects a column, we query the server for the values of that column.

#### Parameters
A dictionary with the name of the axis and the selected column name.

```javascript
{
    "key": "group_by",
    "parameters": "name"
}
```

#### Response
A dictionary with all the values of the requested column (parameters) and the axis name (key)

```javascript
{
    "parameters": ["Host", "vm-1", "vm-2"],
    "key": "group_by"
}
```

***

# Plot
When user finishes selecting the parameters and clicks ok to display the graph, OR, when a preset is selected.

#### Parameters
Dictionary with the required parameters to plot

```javascript
"Line":{
    "y_axis": "performance",
    "x_axis": "timestamp",
    "group_by": {
        "name": ["vm-1","vm-2"]
    }
}
```

#### Response
Dictionary containing the div to insert in the html, and the corresponding js to run (as a string).

```javascript
{
    div:`<div class="bk-root">
                <div class="bk-plotdiv" id="40157552-5d48-4bfa-969e-1f398d7750ef"></div>
         </div>`,
    js: function() {
            var fn = function() {
                Bokeh.safely(function() {
                   var d..
                })
            }
        }
}
```

***

# save
Used when the 'save' button is pressed. 

#### Parameters
Dictionary containing the provided name, and the preset details

```javascript
{
    name:"line",
    preset: "",
    Line: {
        x_axis: "timestamp",
        y_axis: "performance",
        group_by: {
            name: ["vm-1", "vm-2"]}
        }
    }
}
```

#### Response
"preset saved" or server error

***

# load
Used when selecting an experiment, reload preset button clicked, or when changes occur to the preset list (save/delete)

#### Parameters
no parameters ```[]```

#### Response
A dictionary where the key is the given name of the preset, and the value is the paramteres.

```javascript
My_preset:{
    Line: {
        y_axis: "performance",
        x_axis: "timestamp",
        group_by: {
            name: ["vm-1", "vm-2"]
        }
    }
}
```

***

# delete
Used when the 'delete' button is pressed on the preset tab.

#### Parameters
List of strings- names of the selected presets

```javascript
["my_preset", "other_preset"]
```

#### Response
"preset deleted" or server error