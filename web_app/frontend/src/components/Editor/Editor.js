import React from 'react';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/material.css';
import 'codemirror/mode/python/python';
import { Controlled as ControlledEditor } from 'react-codemirror2';
import classes from './Editor.module.css';

const editor = (props) => {

    const {
        displayName,
        value,
        onChange
    } = props;


    function handleChange(editor, data, value){
         onChange(value)
    }

    return(
        <div className={classes.editorContainer}>
            <div className={classes.topPanel}>
                {displayName}
                <button>Maximise</button>
                <button onClick={props.checkCode}>Check Code</button>
            </div>
            <ControlledEditor
                onBeforeChange={handleChange}
                value={value}
                className={classes.codeMirrorWrapper}
                options={{
                    lineWrapping: true,
                    lint: true,
                    mode: 'python',
                    theme: 'material',
                    lineNumbers: true,
                    indentUnit: 4,
                    scrollbarStyle: null,
                    smartIndent: true,
                }}
            
            />
        </div>
    )

}

export default editor;
