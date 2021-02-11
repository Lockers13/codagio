import React, { useState, useEffect } from "react";
import Editor from "@monaco-editor/react";

const monEditor = (props) => {

    useEffect(() => {
        console.log("rendered the editor")
    })

    return(
        <div>
            <Editor
            height="90vh"
            width="50%"
            theme="vs-dark"
            defaultLanguage={props.language}
            defaultValue={props.code}
            onChange={props.onChange}
            />
        </div>
    )
};

export default monEditor;