import React from 'react'
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link
  } from "react-router-dom";
import { LOGIN_ROUTE, USER_SETTINGS_ROUTE, COLLABORATOR_ROUTE, NEW_USER_ROUTE } from './Routes';
import Login from './pages/Login';
import EditUser from './pages/EditUser';
import CollaboratorRegister from './pages/CollaboratorRegister';
import NewUser from './pages/NewUser';

function AppRouter(): JSX.Element {
    return (
        <Router>
            <Switch>
                <Route path={LOGIN_ROUTE}>
                    <Login />
                </Route>
                <Route path={NEW_USER_ROUTE}>
                    <NewUser />
                </Route>
                <Route path={USER_SETTINGS_ROUTE}>
                    <EditUser />
                </Route>
                <Route path={COLLABORATOR_ROUTE}>
                    <CollaboratorRegister />
                </Route>
            </Switch>
        </Router>
    )
}

export default AppRouter;