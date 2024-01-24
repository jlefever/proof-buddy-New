import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from '../pages/Home';
import Login from '../pages/Login';
import Logout from '../pages/Logout'
import SignUp from '../pages/SignUp';
import SignUpUser from '../pages/SignUpUser';
import ForgotPassword from '../pages/ForgotPassword';
import EmailVerification from '../pages/EmailVerification';
import EmailVerificationSuccess from '../pages/EmailVerificationSuccess';
import withAuth from '../hoc/withAuth'
import withNoAuth from '../hoc/withNoAuth'
import EquationalReasoningRacket from '../pages/EquationalReasoningRacket';
import NaturalDeductionFirstOrderLogic from '../pages/NaturalDeductionFirstOrderLogic';
import NaturalDeductionPropositionalLogic from'../pages/NaturalDeductionPropositionalLogic'

const RouteWithNoAuth = ({ component: Component, ...rest }) => {
  const WrappedComponent = withNoAuth(Component);
  return <WrappedComponent {...rest} />;
};

const RouteWithAuth = ({ component: Component }) => {
  const WrappedComponent = withAuth(Component);
  return <WrappedComponent />;
};

const AppRoutes = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home / >} />
        <Route path="/login" element={<RouteWithNoAuth component={Login} />} />
        <Route path="/logout" element={<RouteWithAuth component={Logout} / >} />
        <Route path="/signup" element={<RouteWithNoAuth component={SignUp} />} />
        <Route path="/signup/student" element={<RouteWithNoAuth component={SignUpUser} role="student" / >} />
        <Route path="/signup/instructor" element={<RouteWithNoAuth component={SignUpUser} role="instructor" / >} />
        <Route path="/forgot-password" element={<RouteWithNoAuth component={ForgotPassword} />} />
        <Route path="/verify-email" element={<RouteWithNoAuth component={EmailVerification} / >} />
        <Route path="/verify-success" element={<RouteWithNoAuth component={EmailVerificationSuccess} / >} />
        <Route path="/EquationalReasoningRacket" element={<RouteWithAuth component={EquationalReasoningRacket} / >} />
        <Route path="/NaturalDeductionFirstOrderLogic" element={<RouteWithAuth component={NaturalDeductionFirstOrderLogic} / >} />
        <Route path="/NaturalDeductionPropositionalLogic" element={<RouteWithAuth component={NaturalDeductionPropositionalLogic} / >} />
      </Routes>
    </Router>
  );
};

export default AppRoutes;
