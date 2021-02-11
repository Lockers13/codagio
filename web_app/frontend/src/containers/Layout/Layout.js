import React, { Fragment, Component} from 'react';
import Editor from '../../components/Editor/Editor';
import MonEditor from './Monaco';
import { saveAs } from 'file-saver';

class Layout extends Component {

    state = {
        code: "#Quick recursive fibonnaci\ndef fibonnaci(a,b):\n    if a == 1:\n        return 1\n    else:\n        fibonnaci(a-1,a-2)"
    }

    makePythonFile = () => {
        const tempState = {...this.state}
        const codeString = tempState.code
        let blob = new Blob([codeString], {type: "text/plain;charset=utf-8"});
        console.log(blob)
        saveAs(blob, "test.py")
    }

    codeChangeHandler = (value) => {
        this.setState({code:value})
    }



    render(){
        return(
            <Fragment>
                <div>Toolbar</div>
                <div>Problem Description</div>
                <main>
                    
                    <MonEditor
                        language={"python"}
                        code={this.state.code}
                        onChange = {this.codeChangeHandler}
                    />

                    <Editor
                        language="python" 
                        displayName="Python Editor"
                        value={this.state.code}
                        onChange={this.codeChangeHandler} 
                        checkCode={this.makePythonFile}  
                    /> 

                    <p>File Drop</p>
                    {this.props.children}
                </main>
                <div>Footer</div>
            </Fragment>
        );
    }

}

export default Layout;
