import React, { Fragment, Component} from 'react';
import Editor from '../../components/Editor/Editor';
import Monaco from './Monaco';
import { saveAs } from 'file-saver';

class Layout extends Component {

    state = {
        code: "def fibonnaci():\n    return fibonnaciList"
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
                    {/* <Editor
                        language="python" 
                        displayName="Python Editor"
                        value={this.state.code}
                        onChange={this.codeChangeHandler} 
                        checkCode={this.makePythonFile}  
                    /> */}
                    <Monaco />
                    <p>File Drop</p>
                    {this.props.children}
                </main>
                <div>Footer</div>
            </Fragment>
        );
    }

}

export default Layout;
