<script setup>
    import { ref, onMounted } from "vue";
    import router from "../router/index";

    let csrf_token = ref("");

    let info = ref(false);

    let getCsrfToken = async () => {
    const response = await fetch('/api/v1/csrf-token');
    return response.json();
};

    onMounted(async () => {
        let token = await getCsrfToken();
        csrf_token.value = token.csrf_token;

        info.value = true;
    });


    let loginUser = () => {
    const alert = document.querySelector("#alert");
    let loginForm = document.querySelector('#loginForm');
    let form_data = new FormData(loginForm);

    fetch("/api/v1/auth/login", {
        method: 'POST',
        body: form_data,
        headers: {
            'X-CSRFToken': csrf_token.value
        }
    }).then(function (response) {
        return response.json();
    }).then(function (data) {
        alert.style.display = 'block';
        alert.textContent = data.message ? data.message : data.errors[0];
        router.push('/explore');
    });
}
</script>

<template>
    <div class="alert" id="alert"></div>
    <form v-if="info" @submit.prevent="loginUser" enctype="multipart/form-data" id="loginForm">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" name="username" class="formcontrol">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" name="password" class="formcontrol">
            </div>
           
            <div class="form-group">
                <button type="submit" class="btn btn-register">Login</button>
            </div>
    </form>
</template>