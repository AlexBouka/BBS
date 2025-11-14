import { createRouter, createWebHistory } from "vue-router";

import Login from './components/Login.vue';
import Register from './components/Register.vue';
import RegisterAdmin from './components/RegisterAdmin.vue';
import RouteList from './components/RouteList.vue';
import Route from './components/Route.vue';
import CreateRoute from "./components/CreateRoute.vue";
import CreateBus from "./components/CreateBus.vue";
import Dashboard from "./components/Dashboard.vue";
import UpdateRoute from "./components/UpdateRoute.vue";
import UpdateBus from "./components/UpdateBus.vue";
import Bus from "./components/Bus.vue";
import BusList from "./components/BusList.vue";

const routes = [
    {
        path: '/auth/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/auth/register',
        name: 'Register',
        component: Register
    },
    {
        path: '/auth/register/admin',
        name: 'RegisterAdmin',
        component: RegisterAdmin
    },
    {
        path: '/auth/dashboard',
        name: 'Dashboard',
        component: Dashboard
    },
    {
        path: '/routes/create',
        name: 'CreateRoute',
        component: CreateRoute
    },
    {
        path: '/routes',
        name: 'Routes',
        component: RouteList
    },
    {
        path: '/routes/:id',
        name: 'Route',
        component: Route,
        props: true
    },
    {
        path: '/routes/update/:id',
        name: 'UpdateRoute',
        component: UpdateRoute,
        props: true
    },
    {
        path: '/buses/create',
        name: 'CreateBus',
        component: CreateBus
    },
    {
        path: '/buses',
        name: 'Buses',
        component: BusList
    },
    {
        path: '/buses/:id',
        name: 'Bus',
        component: Bus,
        props: true
    },
    {
        path: '/buses/update/:id',
        name: 'UpdateBus',
        component: UpdateBus,
        props: true
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;
