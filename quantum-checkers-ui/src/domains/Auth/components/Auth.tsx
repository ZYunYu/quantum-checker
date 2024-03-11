import React from 'react';
import Cookies from 'universal-cookie';

interface State {
    username: string;
    password: string;
    error: string;
    isauthenticated: boolean;
}

export class Auth extends React.Component<{}, State> {
    cookies = new Cookies();

    constructor(props: {}) {
        super(props);
        this.state = {
            username: "",
            password: "",
            error: "",
            isauthenticated: false,
        };
    }

    componentDidMount() {
        this.getSession();
    }

    getSession = async () => {
        fetch("/api/session", {
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data: any) => {
            console.log(data);
            if (data.isauthenticated) {
                this.setState({isauthenticated: true});
            } else {
                this.setState({isauthenticated: false});
            }
        })
        .catch((err: Error) => {
            console.log("Error:", err);
        });
    };

    handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        this.setState({password: event.target.value});
    };

    handleUserNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        this.setState({username: event.target.value});
    };

    isResponseOk = (response: Response) => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Network response was not ok.');
        }
    }

    login = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        fetch("/api/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.cookies.get("csrftoken"),
            },
            credentials: "include",
            body: JSON.stringify({
                username: this.state.username,
                password: this.state.password,
            }),
        })
        .then(this.isResponseOk)
        .then((data: any) => {
            console.log(data);
            this.setState({isauthenticated: true, username: "", password: "", error: ""});
        })
        .catch((err: Error) => {
            console.log("Error:", err);
            this.setState({error: "Error logging in"});
        });
    };

    logout = async () => {
        fetch("/api/logout/", {
            credentials: "include",
        })
        .then(this.isResponseOk)
        .then((data: any) => {
            console.log(data);
            this.setState({isauthenticated: false});
        })
        .catch((err: Error) => {
            console.log("Error:", err);
        });
    };
}



