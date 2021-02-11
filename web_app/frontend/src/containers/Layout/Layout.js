import React, { Fragment, Component} from 'react';
import Editor from '../../components/Editor/Editor';
import MonEditor from './Monaco';
import { saveAs } from 'file-saver';

class Layout extends Component {

    state = {
        code: "#test",
        submit: false
    }

    makePythonFile = () => {
        const tempState = {...this.state}
        const codeString = tempState.code
        let blob = new Blob([codeString], {type: "text/plain;charset=utf-8"});
        console.log(blob)
        saveAs(blob, "test.py")
    }

    codeChangeHandler = (value) => {
        if (this.state.submit)
            this.setState({code:value})
        //this.setState({code:value})
    }

    submitStateHandler = () => {
        this.setState({submit:true})
        codeChangeHandler()
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

                    <button onClick={this.submitStateHandler} > Submit code </button>

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
