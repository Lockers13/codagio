import React, { useState } from "react";
import Editor from "@monaco-editor/react";

const MonEditor = (props) => {
  



  return(
      <div>
          <Editor
            height="90vh"
            width="50%"
            theme="vs-dark"
            defaultLanguage={props.language}
            defaultValue={props.code}
         />
      </div>
  )
};

export default MonEditor;