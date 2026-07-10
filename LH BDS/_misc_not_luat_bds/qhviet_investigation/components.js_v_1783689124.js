(()=>{
    Vue.component('loading_ios', {
        template: `
        <div class="spinner">
            <div class="bar1"></div>
            <div class="bar2"></div>
            <div class="bar3"></div>
            <div class="bar4"></div>
            <div class="bar5"></div>
            <div class="bar6"></div>
            <div class="bar7"></div>
            <div class="bar8"></div>
            <div class="bar9"></div>
            <div class="bar10"></div>
            <div class="bar11"></div>
            <div class="bar12"></div>
        </div>
        `
    });

    Vue.component('action_sheet',{
        template: `
            <div class="modal modal-center" @click.stop.prevent="watchClickOutsite($event)">
                <div class="modal-body animate" style="width: auto" ref="modalbody">
                    <div class="wrapper">
                        <div class="quick-items">
                            <div class="title">{{ title }}</div>
                            <template v-for="item in items">
                                <div class="item" :class="item.id == -1 ? 'text-link' : ''" @click.stop.prevent="apply($event,item)">
                                    <template v-if="current_id==item.id">
                                        <svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="check" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" class="svg-inline--fa fa-check fa-w-14 fa-3x"><path fill="currentColor" d="M413.505 91.951L133.49 371.966l-98.995-98.995c-4.686-4.686-12.284-4.686-16.971 0L6.211 284.284c-4.686 4.686-4.686 12.284 0 16.971l118.794 118.794c4.686 4.686 12.284 4.686 16.971 0l299.813-299.813c4.686-4.686 4.686-12.284 0-16.971l-11.314-11.314c-4.686-4.686-12.284-4.686-16.97 0z" class=""></path></svg>
                                    </template>
                                    {{ item.name }}
                                </div>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                callback: null,
                current_id: null,
                title: 'Chọn giá trị',
                items: []
            }
        },
        methods: {
            apply: function(e, item){
                this.close();
                if(typeof this.callback == 'function'){
                    this.callback(item);
                }
            },
            open: function(options){
                this.title = typeof options.title!='undefined' ? options.title : 'Chọn giá trị';
                this.items = typeof options.items!='undefined' ? options.items : [];
                this.callback = typeof options.callback!='undefined' ? options.callback : null;
                this.current_id = typeof options.current_id!='undefined' ? options.current_id : null;
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add("open");
            },
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                    if(typeof this.callback == 'function'){
                        this.callback(null);
                    }
                }
            },
            close: function(){
                this.$el.classList.remove("open");
                this.$el.style.removeProperty('z-index');
            }
        }
    });

    Vue.component('absolute_marker', {
        template: `
            <div class="modal modal-center absolute-marker">
                <div class="modal-body animate">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Thông tin điểm ghim</div>
                    <div class="marker-properties" v-if="marker">
                        <div class="row" v-if="vn2000.x != 0 && vn2000.y != 0 && marker.ward">
                            <div class="label">Tọa độ (VN2000)</div>
                            <div class="value">({{ vn2000.x }}, {{ vn2000.y }})</div>
                        </div>
                        <div class="row" v-if="marker.ward">
                            <div class="label">Trục (VN2000)</div>
                            <div class="value">{{ marker.ward.base_coordinate }}</div>
                        </div>
                        <div class="row" v-for="item in marker.html" v-html="item"></div>
                    </div>
                    <div class="mt-1">
                        <div class="btn btn-primary" @click.stop.prevent="checkPlan()">Xem quy hoạch</div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                marker: null,
                vn2000: {
                    x: 0,
                    y: 0
                }
            }
        },
        methods: {
            open: function(option){

                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.marker = option.marker;

                this.$root.reloadC(this.marker.ward.base_coordinate);

                let key = this.$root.e(atob(this.$root.b),atob(this.$root.a)).inverse([this.marker.point.lng, this.marker.point.lat]);
                this.vn2000 = {
                    x: parseFloat(key[0]).toFixed(4),
                    y: parseFloat(key[1]).toFixed(4)
                }

                this.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
                this.$root.$refs['app-map'].clearParcelMap();
            },
            checkPlan: function(){
                if(this.$root.app_version && this.$root.app_version.code == 2){
                    this.$parent.$refs['app-map'].$refs['province-box'].$refs['province-level-2'].accessPointPosition(this.marker.point);
                }

                if(this.$root.app_version && this.$root.app_version.code == 3){
                    this.$parent.$refs['app-map'].$refs['province-box'].$refs['province-level-3'].accessPointPosition(this.marker.point);
                }

                this.close();
            }
        }
    })
    
    Vue.component('app-header', {
        template: `
            <div class="app-header">
                <div class="app-logo">
                    <img src="/assets/web-v1/images/app-logo.png" />
                </div>
                <div class="app-menu">
                    <ul>
                        <li>
                            <a class="has-icon">Xem quy hoạch <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M12.7071 14.7071C12.3166 15.0976 11.6834 15.0976 11.2929 14.7071L6.29289 9.70711C5.90237 9.31658 5.90237 8.68342 6.29289 8.29289C6.68342 7.90237 7.31658 7.90237 7.70711 8.29289L12 12.5858L16.2929 8.29289C16.6834 7.90237 17.3166 7.90237 17.7071 8.29289C18.0976 8.68342 18.0976 9.31658 17.7071 9.70711L12.7071 14.7071Z"></path> </g></svg></a>
                            <ul>
                                <li @click.stop.prevent="setAppVersion($event, 2)">Hành chính 2 cấp</li>
                                <li @click.stop.prevent="setAppVersion($event, 3)">Hành chính 3 cấp</li>
                            </ul>
                        </li>
                        <li>
                            <a @click.stop.prevent="convertCoor()">Chuyển đổi tọa độ</a>
                        </li>
                        <template v-if="$root.u">
                            <li>
                                <a @click.stop.prevent="grouplist()">Rổ hàng</a>
                            </li>
                            <li>
                                <a @click.stop.prevent="savedlist()">Điểm đã lưu</a>
                            </li>
                            <li>
                                <a @click.stop.prevent="findShareCode()">Mã chia sẻ</a>
                            </li>
                        </template>
                        <li>
                            <a @click.stop.prevent="openTutorial()">Hướng dẫn</a>
                        </li>
                        <li>
                            <a @click.stop.prevent="openDownloadBox()">Tải ứng dụng</a>
                        </li>
                    </ul>
                </div>
                <div class="user-info">
                    <template v-if="$root.u">
                        <div class="account-name">Tài khoản <b>{{ $root.u.phone }}</b> <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M12.7071 14.7071C12.3166 15.0976 11.6834 15.0976 11.2929 14.7071L6.29289 9.70711C5.90237 9.31658 5.90237 8.68342 6.29289 8.29289C6.68342 7.90237 7.31658 7.90237 7.70711 8.29289L12 12.5858L16.2929 8.29289C16.6834 7.90237 17.3166 7.90237 17.7071 8.29289C18.0976 8.68342 18.0976 9.31658 17.7071 9.70711L12.7071 14.7071Z"></path> </g></svg></div>
                        <div class="account-menu">
                            <div class="account-package">
                                <div class="menu-row">
                                    <div class="label">Lượt còn</div>
                                    <div class="value">: {{ $root.u.point }}</div>
                                </div>
                                <div class="menu-row">
                                    <div class="label">Hạn dùng</div>
                                    <div class="value">: {{ $root.u.expired }}</div>
                                </div>
                            </div>
                            <div class="menu-item" @click.stop.prevent="payment($event)">Gia hạn gói cước</div>
                            <div class="menu-item" @click.stop.prevent="savedlist($event)">Điểm đã lưu</div>
                            <div class="menu-item" @click.stop.prevent="grouplist($event)">Rổ hàng</div>
                            <div class="menu-item" @click.stop.prevent="updatePassword($event)">Đổi mật khẩu</div>
                            <div class="menu-item" @click.stop.prevent="logout($event)">Thoát tài khoản</div>
                        </div>
                    </template>
                    <template v-else>
                        <div class="btn btn-primary" @click.stop.prevent="login()">Đăng nhập</div>
                    </template>
                </div>
            </div>
        `,
        methods: {
            convertCoor: function(){
                let vm = this;
                vm.$root.$refs.convertcoor.open({
                    callback: function(f){
                        vm.$root.$refs['app-map'].showAbsolutePoint(f.feature);
                    }
                });
            },
            logout: function(e){
                this.closeMenu(e);
                localStorage.removeItem(x0.xx0('aQ=='));
                window.location.reload();
            },
            updatePassword: function(e){
                this.closeMenu(e);
                this.$root.$refs.changepin.open({});
            },
            closeMenu: function(e){
                e.target.closest('div.account-menu').style.display = "none";
                setTimeout(()=>{
                    e.target.closest('div.account-menu').style.removeProperty('display');
                }, 100);
            },
            findShareCode: function(){
                if(this.$root.app_version && this.$root.app_version.code == 2){
                    this.$parent.$refs['app-map'].$refs['province-box'].$refs['province-level-2'].openShareCodeBox();
                }

                if(this.$root.app_version && this.$root.app_version.code == 3){
                    this.$parent.$refs['app-map'].$refs['province-box'].$refs['province-level-3'].openShareCodeBox();
                }
            },
            grouplist: function(e){
                if(e){
                    this.closeMenu(e);
                }

                this.$root.$refs.grouplist.open({});
            },
            savedlist: function(e){
                if(e){
                    this.closeMenu(e);
                }
                this.$root.$refs.savedlist.open({});
            },
            payment: function(e){
                this.closeMenu(e);
                this.$root.$refs.payment.open({
                    has_reset: false
                });
            },
            login: function(){
                this.$root.$refs.login.open({
                    callback: function(){
                        
                    }
                });
            },
            setAppVersion: function(e, code){
                this.$root.setAppVersion(code);
                e.target.closest('ul').style.display = "none";
                setTimeout(()=>{
                    e.target.closest('ul').style.display = "block";
                }, 100);
            },
            openDownloadBox: function(){
                this.$root.$refs['download-app'].open();
            },
            openTutorial: function(){
                this.$root.$refs['tutorial'].open();
            }
        },
        mounted: function(){
            
        }
    });

    Vue.component('changepin', {
        template: `
            <div class="modal modal-center">
                <div class="modal-body animate">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Cập nhật mật khẩu</div>
                    <div>Nhập mật khẩu mới cần cập nhật vào khung bên dưới sau đó nhấn xác nhận để cập nhật mật khẩu</div>
                    <div class="login">
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <label class="sub-title">Mật khẩu cũ</label>
                                <div style="position:relative;">
                                    <input type="password" ref="old_passwordinput" v-model="form.old_pin">
                                    <div class="absolute-input-icon" @click.stop.prevent="viewOldPassword($event)">
                                        <svg v-if="old_type == 'password'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M279.6 160.4C282.4 160.1 285.2 160 288 160C341 160 384 202.1 384 256C384 309 341 352 288 352C234.1 352 192 309 192 256C192 253.2 192.1 250.4 192.4 247.6C201.7 252.1 212.5 256 224 256C259.3 256 288 227.3 288 192C288 180.5 284.1 169.7 279.6 160.4zM480.6 112.6C527.4 156 558.7 207.1 573.5 243.7C576.8 251.6 576.8 260.4 573.5 268.3C558.7 304 527.4 355.1 480.6 399.4C433.5 443.2 368.8 480 288 480C207.2 480 142.5 443.2 95.42 399.4C48.62 355.1 17.34 304 2.461 268.3C-.8205 260.4-.8205 251.6 2.461 243.7C17.34 207.1 48.62 156 95.42 112.6C142.5 68.84 207.2 32 288 32C368.8 32 433.5 68.84 480.6 112.6V112.6zM288 112C208.5 112 144 176.5 144 256C144 335.5 208.5 400 288 400C367.5 400 432 335.5 432 256C432 176.5 367.5 112 288 112z"/></svg>
                                        <svg v-if="old_type != 'password'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M150.7 92.77C195 58.27 251.8 32 320 32C400.8 32 465.5 68.84 512.6 112.6C559.4 156 590.7 207.1 605.5 243.7C608.8 251.6 608.8 260.4 605.5 268.3C592.1 300.6 565.2 346.1 525.6 386.7L630.8 469.1C641.2 477.3 643.1 492.4 634.9 502.8C626.7 513.2 611.6 515.1 601.2 506.9L9.196 42.89C-1.236 34.71-3.065 19.63 5.112 9.196C13.29-1.236 28.37-3.065 38.81 5.112L150.7 92.77zM223.1 149.5L313.4 220.3C317.6 211.8 320 202.2 320 191.1C320 180.5 316.1 169.7 311.6 160.4C314.4 160.1 317.2 159.1 320 159.1C373 159.1 416 202.1 416 255.1C416 269.7 413.1 282.7 407.1 294.5L446.6 324.7C457.7 304.3 464 280.9 464 255.1C464 176.5 399.5 111.1 320 111.1C282.7 111.1 248.6 126.2 223.1 149.5zM320 480C239.2 480 174.5 443.2 127.4 399.4C80.62 355.1 49.34 304 34.46 268.3C31.18 260.4 31.18 251.6 34.46 243.7C44 220.8 60.29 191.2 83.09 161.5L177.4 235.8C176.5 242.4 176 249.1 176 255.1C176 335.5 240.5 400 320 400C338.7 400 356.6 396.4 373 389.9L446.2 447.5C409.9 467.1 367.8 480 320 480H320z"/></svg>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <label class="sub-title">Mật khẩu mới</label>
                                <div style="position:relative;">
                                    <input type="password" ref="passwordinput" v-model="form.new_pin">
                                    <div class="absolute-input-icon" @click.stop.prevent="viewPassword($event)">
                                        <svg v-if="type == 'password'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M279.6 160.4C282.4 160.1 285.2 160 288 160C341 160 384 202.1 384 256C384 309 341 352 288 352C234.1 352 192 309 192 256C192 253.2 192.1 250.4 192.4 247.6C201.7 252.1 212.5 256 224 256C259.3 256 288 227.3 288 192C288 180.5 284.1 169.7 279.6 160.4zM480.6 112.6C527.4 156 558.7 207.1 573.5 243.7C576.8 251.6 576.8 260.4 573.5 268.3C558.7 304 527.4 355.1 480.6 399.4C433.5 443.2 368.8 480 288 480C207.2 480 142.5 443.2 95.42 399.4C48.62 355.1 17.34 304 2.461 268.3C-.8205 260.4-.8205 251.6 2.461 243.7C17.34 207.1 48.62 156 95.42 112.6C142.5 68.84 207.2 32 288 32C368.8 32 433.5 68.84 480.6 112.6V112.6zM288 112C208.5 112 144 176.5 144 256C144 335.5 208.5 400 288 400C367.5 400 432 335.5 432 256C432 176.5 367.5 112 288 112z"/></svg>
                                        <svg v-if="type != 'password'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M150.7 92.77C195 58.27 251.8 32 320 32C400.8 32 465.5 68.84 512.6 112.6C559.4 156 590.7 207.1 605.5 243.7C608.8 251.6 608.8 260.4 605.5 268.3C592.1 300.6 565.2 346.1 525.6 386.7L630.8 469.1C641.2 477.3 643.1 492.4 634.9 502.8C626.7 513.2 611.6 515.1 601.2 506.9L9.196 42.89C-1.236 34.71-3.065 19.63 5.112 9.196C13.29-1.236 28.37-3.065 38.81 5.112L150.7 92.77zM223.1 149.5L313.4 220.3C317.6 211.8 320 202.2 320 191.1C320 180.5 316.1 169.7 311.6 160.4C314.4 160.1 317.2 159.1 320 159.1C373 159.1 416 202.1 416 255.1C416 269.7 413.1 282.7 407.1 294.5L446.6 324.7C457.7 304.3 464 280.9 464 255.1C464 176.5 399.5 111.1 320 111.1C282.7 111.1 248.6 126.2 223.1 149.5zM320 480C239.2 480 174.5 443.2 127.4 399.4C80.62 355.1 49.34 304 34.46 268.3C31.18 260.4 31.18 251.6 34.46 243.7C44 220.8 60.29 191.2 83.09 161.5L177.4 235.8C176.5 242.4 176 249.1 176 255.1C176 335.5 240.5 400 320 400C338.7 400 356.6 396.4 373 389.9L446.2 447.5C409.9 467.1 367.8 480 320 480H320z"/></svg>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="d-flex">
                            <button class="btn btn-primary mr-1 flex-1" @click.stop.prevent="update($event)">{{ sending ? 'Đang lưu...' : 'Cập nhật' }}</button>
                            <button class="btn btn-default flex-1" @click.stop.prevent="cancel($event)">Hủy thao tác</button>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                form: {
                    old_pin: '',
                    new_pin: ''
                },
                old_type: 'password',
                type: 'password',
                callback: null,
                sending: false
            }
        },
        methods: {
            viewOldPassword: function(e){
                this.$refs.old_passwordinput.type = this.$refs.old_passwordinput.type == 'text' ? 'password' : 'text';
                this.old_type = this.old_type == 'password' ? 'text' : 'password';
            },
            viewPassword: function(e){
                this.$refs.passwordinput.type = this.$refs.passwordinput.type == 'text' ? 'password' : 'text';
                this.type = this.type == 'password' ? 'text' : 'password';
            },
            update: function(e){
                let vm = this;
                vm.sending = true;
                vm.$root.postData(vm.$root.setting.api_resource.update_pin, vm.form).then(res => {
                    vm.sending = false;
                    if(!res.error){
                        if(typeof vm.callback == 'function'){
                            vm.callback();
                        }
                        vm.close(e);
                    }
                    vm.$root.showMessageBox(res.message);
                });
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.form = option && typeof option.form != 'undefined' ? option.form : {
                    old_pin: '',
                    new_pin: ''
                };
                this.$el.classList.add('open');
            },
            cancel: function(e){
                this.$root.ontap(e, ()=>{
                    if(typeof this.callback == 'function'){
                        this.callback();
                    }
                    this.$el.classList.remove('open');
                    this.$el.style.removeProperty('z-index');
                })
            },
            close: function(e) {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        }
    }); 

    Vue.component('download-app', {
        template: `
            <div class="modal">
                <div class="modal-body animate">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Tải ứng dụng di động</div>
                    <div class="download">
                        <div class="mb-1">Vui lòng sử dụng thiết bị di động quét mã QR dưới đây hoặc nhấp vào biểu tượng App Store(dành cho IOS), Google Play(dành cho Android) để tải và cài đặt ứng dụng trên thiết bị</div>
                        <div class="d-flex">
                            <div class="flex-1 store-icon mt-1">
                                <div class="ios-store">
                                    <a :href="appstore"><img src="/assets/web-v1/images/mobile-store.png" /></a>
                                </div>
                                <div class="android-store">
                                    <a :href="chplay"><img src="/assets/web-v1/images/mobile-store.png" /></a>
                                </div>
                            </div>
                            <div class="flex-1 qr-icon mt-1">
                                <img src="/assets/web-v1/images/qr-download.svg" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                appstore: 'https://apps.apple.com/us/app/quy-ho%E1%BA%A1ch-vi%E1%BB%87t/id1623342465',
                chplay: 'https://play.google.com/store/apps/details?id=com.app.qhviet'
            }
        },
        methods: {
            open: function(){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        watch: {
            appstore: function(newval){
                if(newval != ''){
                    setTimeout(()=>{
                        if(window.screen.availWidth < 1024){
                            this.open();
                        }
                    }, 100)
                }
            }
        }
    });

    Vue.component('tutorial', {
        template: `
            <div class="modal modal-center">
                <div class="modal-body lg animate">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Hướng dẫn sử dụng</div>
                    <div class="tutorial-body">
                        <div class="tutorial-tabs">
                            <template v-for="(item, index) in tutorial">
                                <div class="item" :class="active == index ? 'active' : ''">
                                    <div class="tab-title" @click.stop.prevent="changeIndex($event, index)">
                                        <div class="text">{{ index+1 }}. {{ item.name }}</div>
                                        <div class="icon">
                                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path d="M192 384c-8.188 0-16.38-3.125-22.62-9.375l-160-160c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L192 306.8l137.4-137.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-160 160C208.4 380.9 200.2 384 192 384z"/></svg>
                                        </div>
                                    </div>
                                    <div class="tab-content" v-html="item.content"></div>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                active: -1,
                tutorial: [
                    {
                        name: `Xem bản đồ quy hoạch`,
                        content: `
                        <div class="row">
                            <div class="step">Bước 1:</div>
                            <div class="step-text">Nhấn vào chọn Tỉnh</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 2:</div>
                            <div class="step-text">Chọn  Huyện > Chọn Xã</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 3:</div>
                            <div class="step-text">Hệ thống sẽ hiển thị bản đồ theo khu vực mình đã chọn. Dựa vào <b>màu sắc & ký hiệu</b> trên bản đồ, đối chiếu với mục <b>“Chú giải”</b> để xác định quy hoạch loại đất gì.</div>
                        </div>
                        <div class="step-text"><b>** Lưu ý:</b></div>
                        <div class="step-text">1. Khác biệt giữa Quy hoạch và kế hoạch.</div>
                        <div class="row">
                            <div class="step">Quy hoạch sử dụng đất:</div>
                            <div class="step-text">là việc phân bổ và khoanh vùng đất đai theo không gian sử dụng cho các mục tiêu phát triển kinh tế - xã hội, quốc phòng, an ninh, bảo vệ môi trường và thích ứng biến đổi khí hậu trên cơ sở tiềm năng đất đai và nhu cầu sử dụng đất của các ngành, lĩnh vực đối với từng vùng kinh tế - xã hội và đơn vị hành chính trong một khoảng thời gian xác định. Quy hoạch sử dụng đất thông thường là 10 năm.</div>
                        </div>
                        <div class="row">
                            <div class="step">Kế hoạch sử dụng đất:</div>
                            <div class="step-text">là việc phân chia quy hoạch sử dụng đất theo thời gian để thực hiện trong kỳ quy hoạch sử dụng đất, kế hoạch sử dụng đất thường có hằng năm hoặc 5 năm tùy địa phương.</div>
                        </div>
                        <div class="step-text">- Thông thường trên bản đồ kế hoạch sử dụng đất sẻ thể hiện khu vực sẻ thực hiện kế hoạch trong năm hoặc 5 năm tới bằng những đường kẻ sọc đỏ trên màu nền đất Quy hoạch.</div>
                        <div class="step-text">- Còn lại các phần không có kẻ sọc sẻ dựa trên bản đồ Quy hoạch hoặc kế hoạch 5 năm đã được phê duyệt trước đó.</div>
                        <div class="row">
                            <div class="step">Ví dụ:</div>
                            <div class="step-text">Kế hoạch sử dụng đất Thành phố Thủ Đức 2021: Sổ 2018 đã là đất ở, nhưng khi kiểm tra thì vị trí lô đất thể hiện trên bản đồ kế hoạch sử dụng đất 2021 vẫn còn là đất nông nghiệp. Lý do là vị trí lô đất không nằm trong vùng sọc đỏ (vùng triển khai quy hoạch từ 2021) và tới thời điểm hiện tại thành phố Thủ Đức chưa phê duyệt Quy hoạch sử dụng đất 2030 hoặc kế hoạch sử dụng đất 2025. Nên phần đất xem trên bản đồ đang áp dụng là kế hoạch sử dụng đất đến năm 2020 theo Quyết định Số: 2354/QĐ-UBND phê duyệt ngày 16 tháng 05 năm 2014 (hiện đang hết thời hạn).</div>  
                        </div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/huongdan.png" style="max-width:100%;" /></div>
                        <div class="step-text">2. Ngày tháng năm phê duyệt Kế hoạch hoặc Quy hoạch sử dụng đất.</div>
                        <div class="step-text">3. Nguyên tắc để lập quy hoạch là đất ở thì phải đi cùng với giao thông (đường). Nếu đất của bạn có quy hoạch là đất ở, nhưng bản đồ quy hoạch không thể hiện đường giao thông cho khu vực này thì bạn nên kiểm tra lại xem đất của bạn có thuộc Quy hoạch dự án Khu dân cư không? </div>
                        <div class="step-text">4. Đất cạnh sông, suối... thì cần kiểm tra hành lang bảo vệ sông, suối là bao nhiêu m?</div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/quyhoachkdc.PNG" style="max-width:100%;" /></div>
                        `
                    },
                    {
                        name: `Tra cứu theo số tờ thửa`,
                        content: `
                        <div class="row">
                            <div class="step">Bước 1:</div>
                            <div class="step-text">Nhấn vào chọn chọn Tỉnh > Chọn Huyện > Chọn Xã</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 2:</div>
                            <div class="step-text">Sau khi bản đồ hiện ra nhấn vào nút "<b>Kiểm tra</b>"</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 3:</div>
                            <div class="step-text">Chọn vào tab "<b>Số tờ thửa</b>"</div>
                        </div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/tothua.PNG" style="border: 1px solid #999;" /></div>
                        <div class="row mt-1">
                            <div class="step">Bước 4:</div>
                            <div class="step-text">Nhập vào khung "<b>Mã số tờ</b>" và "<b>Mã số thửa</b>" theo như trên sổ ghi</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 5:</div>
                            <div class="step-text">Nhấn nút "<b>Kiểm tra</b>"</div>
                        </div>
                        <div class="row">
                            <div class="step">Ghi chú:</div>
                            <div class="step-text">Nếu tra theo tờ thửa không có dữ liệu thì nhìn sang bản vẽ <b>sơ đồ thửa đất</b> trên sổ tra theo các thửa bên cạnh "số thửa nhỏ nhất" rồi dựa theo đó xác định vị trí thửa của mình.</div>                                    
                        </div>
                        <div class="row">
                            <div class="step"><b>**Lưu ý:</b></div>
                        </div>
                        <div class="step-text">
                            <div class="step-text">1. Nguyên tắc để lập quy hoạch là đất ở thì phải đi cùng với giao thông (đường). Nếu đất của bạn có quy hoạch là đất ở, nhưng bản đồ quy hoạch không thể hiện đường giao thông cho khu vực này thì bạn nên kiểm tra lại xem đất của bạn có thuộc Quy hoạch dự án Khu dân cư không? </div>
                            <div class="step-text">2. Đất cạnh sông, suối... thì cần kiểm tra hành lang bảo vệ sông, suối là bao nhiêu m?</div>
                        </div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/quyhoachkdc.PNG" style="max-width:100%;" /></div>
                        `
                    },
                    {
                        name: `Tra cứu theo bảng góc ranh`,
                        content: `
                        <div class="row">
                            <div class="step">Bước 1:</div>
                            <div class="step-text">Nhấn vào chọn chọn Tỉnh > Chọn Huyện > Chọn Xã</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 2:</div>
                            <div class="step-text">Sau khi bản đồ hiện ra nhấn vào nút "<b>Kiểm tra</b>"</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 3:</div>
                            <div class="step-text">Chọn vào tab "<b>Bảng góc ranh</b>"</div>
                        </div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/gocranh.PNG" style="border: 1px solid #999;max-width:100%;" /></div>
                        <div class="row mt-1">
                            <div class="step">Bước 4:</div>
                            <div class="step-text">Nhấn vào "<b>Quét tọa độ từ ảnh</b>" sau đó chọn ảnh có bảng tọa độ góc ranh</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 5:</div>
                            <div class="step-text">Sau khi ảnh được chọn di chuyển hình ảnh sao cho bảng tọa độ góc ranh nằm ở trong khu vực khung chọn</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 6:</div>
                            <div class="step-text">Nhấn nút "<b>Xác nhận</b>" và chờ kết quả đọc ảnh</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 7:</div>
                            <div class="step-text">Nếu đọc ảnh thành công thì tọa độ được quét trong ảnh sẽ tự nhập vào bảng tọa độ.</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 8:</div>
                            <div class="step-text">Kiểm tra bằng mắt xem tọa độ đọc được từ ảnh có đúng chưa (vì có thể kết quả đọc có sai sót chất lượng ảnh ko được tốt). Sau đó nhấn nút "<b>Kiểm tra</b>"</div>
                        </div>
                        <div class="step-text"><b>** Lưu ý:</b></div>
                        <div class="step-text">1. Nguyên tắc để lập quy hoạch là đất ở thì phải đi cùng với giao thông (đường). Nếu đất của bạn có quy hoạch là đất ở, nhưng bản đồ quy hoạch không thể hiện đường giao thông cho khu vực này thì bạn nên kiểm tra lại xem đất của bạn có thuộc Quy hoạch dự án Khu dân cư không? </div>
                        <div class="step-text">2. Đất cạnh sông, suối... thì cần kiểm tra hành lang bảo vệ sông, suối là bao nhiêu m?</div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/quyhoachkdc.PNG" style="max-width:100%;" /></div>
                        `
                    },
                    {
                        name: `Tra cứu theo nền vệ tinh`,
                        content: `
                        <div class="row">
                            <div class="step">Bước 1:</div>
                            <div class="step-text">Nhấn vào chọn Tỉnh > Chọn Huyện > Chọn Xã</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 2:</div>
                            <div class="step-text">Kéo thanh kéo bên phải xuống dưới cùng để ẩn đi lớp nền quy hoạch</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 3:</div>
                            <div class="step-text">Nhấn vào biểu tượng "<b>Vệ tinh</b>" ở góc trên bên phải</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 4:</div>
                            <div class="step-text">Dựa theo nền vệ tinh tìm vị trí muốn kiểm tra</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 5:</div>
                            <div class="step-text">Sau khi xác định được vị trí đất trên nền vệ tinh rồi thì nhấn nút "<b>Thước đo</b>"</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 6:</div>
                            <div class="step-text">Sử dụng công cụ thước đo khoanh vùng khu đất</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 7:</div>
                            <div class="step-text">Kéo thanh kéo nền bên phải lên lại để hiển thị lớp nền quy hoạch sau đó xem quy hoạch</div>
                        </div>
                        <div class="step-text"><b>** Lưu ý:</b></div>
                        <div class="step-text">1. Nguyên tắc để lập quy hoạch là đất ở thì phải đi cùng với giao thông (đường). Nếu đất của bạn có quy hoạch là đất ở, nhưng bản đồ quy hoạch không thể hiện đường giao thông cho khu vực này thì bạn nên kiểm tra lại xem đất của bạn có thuộc Quy hoạch dự án Khu dân cư không? </div>
                        <div class="step-text">2. Đất cạnh sông, suối... thì cần kiểm tra hành lang bảo vệ sông, suối là bao nhiêu m?</div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/quyhoachkdc.PNG" style="max-width:100%;" /></div>
                        `
                    },
                    {
                        name: `Tra cứu theo tọa độ Google`,
                        content: `
                        <div class="row">
                            <div class="step">Bước 1:</div>
                            <div class="step-text">Nhấn vào chọn chọn Tỉnh > Chọn Huyện > Chọn Xã</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 2:</div>
                            <div class="step-text">Sau khi bản đồ hiện ra nhấn vào nút "<b>Kiểm tra</b>"</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 3:</div>
                            <div class="step-text">Chọn vào tab "<b>Tọa độ Google</b>"</div>
                        </div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/google.png" style="border: 1px solid #999;max-width:100%;" /></div>
                        <div class="row mt-1">
                            <div class="step">Bước 4:</div>
                            <div class="step-text">Nhập vào tọa độ lng, lat vào khung bên dưới sau đó nhấn <b>“Kiểm tra”</b> </div>
                        </div>
                        <div class="step-text"><b>** Lưu ý:</b></div>
                        <div class="step-text">1. Nguyên tắc để lập quy hoạch là đất ở thì phải đi cùng với giao thông (đường). Nếu đất của bạn có quy hoạch là đất ở, nhưng bản đồ quy hoạch không thể hiện đường giao thông cho khu vực này thì bạn nên kiểm tra lại xem đất của bạn có thuộc Quy hoạch dự án Khu dân cư không? </div>
                        <div class="step-text">2. Đất cạnh sông, suối... thì cần kiểm tra hành lang bảo vệ sông, suối là bao nhiêu m?</div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/quyhoachkdc.PNG" style="max-width:100%;" /></div>
                        `
                    },
                    {
                        name: `Lấy mã chia sẻ vị trí`,
                        content: `
                        <div class="row">
                            <div class="step">Bước 1:</div>
                            <div class="step-text">Nhấn vào chọn Tỉnh > Chọn Huyện > Chọn Xã</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 2:</div>
                            <div class="step-text">Tìm thửa đất muốn lấy mã chia sẻ theo tờ thửa hoặc theo góc ranh theo hướng dẫn tra cứu theo tờ thửa & góc ranh</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 3:</div>
                            <div class="step-text">Sau khi tìm được thửa đất nhấn "<b>Mã chia sẻ</b>" tại khung "<b>Thông tin thửa</b>"</div>
                        </div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/machiase_desktop.JPG" style="border: 1px solid #999;max-width:100%" /></div>
                        <div class="row mt-1">
                            <div class="step">Bước 4:</div>
                            <div class="step-text">Mã chia sẻ sau khi được tạo sẽ hiển thị lên màn hình</div>
                        </div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/machiase_1_desktop.JPG" style="border: 1px solid #999;max-width:100%" /></div>
                        <div class="row mt-1">
                            <div class="step">Bước 5:</div>
                            <div class="step-text">Nhấn nút "<b>Copy mã</b>" và gửi cho người bạn muốn chia sẻ vị trí</div>
                        </div>
                        `
                    },
                    {
                        name: `Sử dụng mã chia sẻ vị trí`,
                        content: `
                        <div class="row">
                            <div class="step">Bước 1:</div>
                            <div class="step-text">Nhấn vào menu "<b>Mã chia sẻ</b>" tại trang chủ</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 2:</div>
                            <div class="step-text">Nhập mã chia sẻ nhận được từ bạn bè vào khung mã chia sẻ</div>
                        </div>
                        <div class="row">
                            <div class="step">Bước 3:</div>
                            <div class="step-text">Nhấn nút "<b>Xác nhận</b>"</div>
                        </div>
                        `
                    },
                    {
                        name: `Các chức năng khác`,
                        content: `
                        <div class="row">
                            <div class="step">Thước đo:</div>
                            <div class="step-text">Nhấn vào nút "<b>Bật thước đo</b>" để mở chức năng đo khoảng cách giữa các điểm trên bản đồ quy hoạch</div> 
                        </div>
                        <div class="row mt-1"><img src="/assets/web-v1/images/hd/chucnangphu.png" style="max-width:100%;" /></div>
                        <div class="row">
                            <div class="step">Điểm đã lưu:</div>
                            <div class="step-text">để lưu trữ các điểm đã lưu</div>
                        </div>
                        `
                    }
                ]
            }
        },
        methods: {
            changeIndex: function(event, index){
                event.target.classList.add("ontap");
                setTimeout(()=>{
                    event.target.classList.remove("ontap");
                    if(this.active == index){
                        this.active = -1;
                    }else{
                        this.active = index;
                    }
                }, 100);
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            close: function(event) {
                if(event){
                    event.target.classList.add("ontap");
                    setTimeout(()=>{
                        event.target.classList.remove("ontap");
                        this.$el.classList.remove('open');
                    }, 100);
                }else{
                    this.$el.classList.remove('open');
                }

                this.$el.style.removeProperty('z-index');

                let hashURL = location.hash.replaceAll(/\#/ig, '');
                if(hashURL == 'tutorial'){
                    location.replace(location.origin);
                }
            }
        }
    });

    Vue.component('change-base-layer', {
        template: `
            <div class="change-base-layer" @click.stop.prevent="changeBaseLayer()">
                <div class="layer-icon">
                    <img src="/assets/web-v1/images/ve-tinh.png" v-if="$parent.maptype != 'street'" />
                    <img src="/assets/web-v1/images/giao-thong.png" v-if="$parent.maptype == 'street'" />
                </div>
                <div class="layer-name">{{ $parent.maptype == 'street' ? 'Giao thông' : 'Vệ tinh' }}</div>
            </div>
        `,
        methods: {
            changeBaseLayer: function(){
                if(this.$parent.maptype != 'street'){
                    this.$parent.changeMapType('street')
                }else{
                    this.$parent.changeMapType('satellite')
                }
            }
        }
    });

    Vue.component('map-note', {
        template: `<div class="map-note">Thông tin quy hoạch hiển thị trên website chỉ mang giá trị tham khảo</div>`
    });

    Vue.component('app-map', {
        template: `
        <div class="lmap">
            <!-- Bản đồ -->
            <div ref="gmap" class="gmap"></div>

            <!-- Thanh chức năng  -->
            <map-tools ref="map-tool"></map-tools>

            <!-- Bảng thông tin thửa -->
            <parcel-properties ref="properties_box" :parcel="parcel" v-if="parcel.is_show && !is_draw_ruler"></parcel-properties>

            <!-- Bảng thông tin thước đo -->
            <ruler-box ref="ruler_box" :ruler="ruler" v-if="is_draw_ruler"></ruler-box>

            <!-- Danh sách tỉnh thành -->
            <province-box ref="province-box"></province-box>

            <!-- Khung chuyển đổi nền vệ tinh / giao thông -->
            <change-base-layer></change-base-layer>

            <!-- Ghi chú map -->
            <map-note></map-note>
        </div>
        `,
        data: function(){
            return {
                maptype: 'street',
                ward: null,
                feature: null,
                province: null,
                selected_layer_id: null,
                option_layers: [],
                layers: [],
                object_layers: [],
                opacity: 8,
                boundaryPolygon: null,
                is_draw_ruler: false,
                ruler: {
                    layers: [],
                    layer_points: [],
                    features: [],
                    show_distance: true,
                    is_collapsed: false,
                    drawing_feature: null
                },
                parcel: {
                    is_show: false,
                    layer: null,
                    geometry: null,
                    is_finding: false,
                    is_checking_plan: false,
                    show_distance: true,
                    show_parcel_label: false,
                    properties: [],
                    plan_id: null,
                    plan_info: [],
                    plan_detail: [],
                    parcel_labels_layer: [],
                    show_saved_feature: false,
                    area: 0
                },
                my_location: {
                    point: null,
                    layer: null
                }
            }
        },
        methods: {
            clearParcelMap: function(){
                if(this.parcel.layer){
                    this.parcel.layer.remove();
                    this.parcel.layer = null;
                }
            },
            showAbsolutePoint: function(feature){
                this.drawParcel(feature);
                this.convertPlace(feature.geometry);
            },
            convertPlace: function(geometry){
                let vm = this;
                let centerPoint = vm.$root.getCenterGeometry(geometry);
                vm.$root.postData(vm.$root.setting.api_resource.convert_place_id_level_3, {
                    lng: centerPoint.lng,
                    lat: centerPoint.lat
                }).then((res)=>{
                    if(!res.error && res.data){
                        vm.$root.$refs.absolute_marker.open({
                            marker: res.data
                        });
                    }else{
                        vm.$root.showMessageBox('Không thể xác định vị trí dựa theo tọa độ hiện tại của bạn .');
                    }
                });
            },
            setMap: function(option){
                let vm = this;
                vm.boundaryPolygon = null;
                vm.clearParcelMap();
                vm.$root.$refs.absolute_marker.close();

                vm.ward = option.ward;
                vm.province = option.province;
                vm.my_location.point = option.hasOwnProperty('my_location') ? option.my_location : null;
                vm.parcel.show_saved_feature = option.hasOwnProperty('show_saved_feature') ? option.show_saved_feature : false;
                window.my_feature = option.hasOwnProperty('feature') ? option.feature : null;

                window.callbackAfterInitMap = function(){
                    if(window.my_feature){
                        vm.drawParcel(window.my_feature);
                        vm.getProperties(window.my_feature).then(()=>{
                            vm.checkPlan();
                        });
                    }
                    
                    if(vm.my_location){
                        vm.drawMyLocation();
                    }
                }

                vm.loadLayers();
                vm.$refs['province-box'].$el.classList.add('hide');
            },
            loadLayers: function(){
                let vm = this;
                vm.loading_layers = true;
                let layerURL = vm.ward.level == 2 ? vm.$root.setting.api_resource.layers : vm.$root.setting.api_resource.layers_level_3;
                vm.$root.postData(layerURL, {
                    ward_id: vm.ward.id
                }).then(res => {
                    vm.loading_layers = false;
                    if(!res.error){
                        let wardLayers = res.data.ward_layers.map((layer)=>{
                            layer.config = JSON.parse(layer.config);
                            layer.ward_name = window.removeFirstPart(layer.ward_name);
                            layer.name =  window.replaceDistrictKeywords(layer.ward_name) + ' - ' + layer.name;
                            return layer;
                        });

                        vm.option_layers = res.data.district_layers.map((layer)=>{
                            layer.config = JSON.parse(layer.config);
                            let disname = layer.dis_name.split('-');
                            disname = window.replaceDistrictKeywords(disname[disname.length - 1].trim());

                            layer.name =  disname + ' - ' + layer.name;
                            layer.map_type = 'default';
                            return layer;
                        }).concat(wardLayers);

                        if(vm.ward.hasOwnProperty('default_option_id')){
                            let findIndex = res.data.district_layers.findIndex((e)=>{
                                return e.id == vm.ward.default_option_id;
                            });
                            if(findIndex > -1){
                                vm.selected_layer_id = vm.ward.default_option_id;
                            }else{
                                let findIndex1 = res.data.district_layers.findIndex((e)=>{
                                    return parseInt(e.isDefault) == 1;
                                });
                                vm.selected_layer_id = findIndex1 > -1 ? res.data.district_layers[findIndex1].id : res.data.district_layers[0].id;
                            }
                        }else{
                            let findIndex = res.data.district_layers.findIndex((e)=>{
                                return parseInt(e.isDefault) == 1;
                            });
                            vm.selected_layer_id = findIndex > -1 ? res.data.district_layers[findIndex].id : res.data.district_layers[0].id;
                        }

                        res.data.feature.center = JSON.parse(res.data.feature.center);
                        res.data.feature.geom = JSON.parse(res.data.feature.geom);
                        vm.feature = res.data.feature;

                        vm.object_layers = res.data.object_layers;
                        setTimeout(()=>{
                            vm.reloadLayer();
                        }, 100)
                    }else{
                        if(res.hasOwnProperty('message')){
                            vm.$root.showMessageBox(res.message);
                        }
                    }
                }).catch((msg)=>{
                    
                });
            },
            getCurrentLocation: function(e){
                let vm = this;
                window.bridge.call('getCurrentLocation', {}, function(position){
                    if(typeof position == 'object'){
                        vm.my_location.point = position;
                        vm.drawMyLocation().then(()=>{
                            let current_zoom = vm.map.getZoom() > 16 ? vm.map.getZoom() : 18;
                            vm.map.setView([vm.my_location.point.lat, vm.my_location.point.lng], current_zoom);
                        });
                    }    
                });
            },
            changeLayerOpacity: function(){
                for (let index = 0; index < this.layers.length; index++) {
                    this.layers[index].setOpacity(this.opacity == 0 ? 0 : this.opacity / 10);
                }
            },
            viewCoordinateParcel: function(e){
                let vm = this;
                let mainProvince = vm.province.hasOwnProperty('childs') ? vm.province.childs.find(item => item.is_main) : vm.province;
                if(mainProvince){
                    vm.$root.reloadC(mainProvince.base_coordinate);
                    let points = JSON.parse(JSON.stringify(vm.parcel.geometry.coordinates[0]));
                    points = points.map((point)=>{
                        let lng = point[0];
                        let lat = point[1];

                        let vn2000Point = vm.$root.e(atob(vm.$root.b),atob(vm.$root.a)).inverse([lng, lat]);
                        return {
                            lng: Number(lng.toFixed(10)),
                            lat: Number(lat.toFixed(10)),
                            x: Number(vn2000Point[0].toFixed(3)),
                            y: Number(vn2000Point[1].toFixed(3))
                        };
                    });

                    vm.$root.$refs.coordinatetable.open({
                        points: points,
                        base_coordinate: mainProvince.base_coordinate,
                        items: vm.province.hasOwnProperty('childs') ? vm.province.childs : [vm.province]
                    });
                }
            },
            resetParcel: function(){
                this.parcel.geometry = null;
                this.parcel.properties = [];
                this.parcel.is_show = false;
                this.parcel.plan_id = null;
                this.parcel.plan_info = [];
                this.parcel.plan_detail = [];
            },
            openCheckParcel: function(e){
                let vm = this;
                vm.$root.$refs.checkparcel.open({
                    province: vm.province,
                    ward: vm.ward,
                    callback: function(result){
                        if(result.feature){
                            vm.$refs['province-box'].$el.classList.add('hide');

                            vm.parcel.geometry = result.feature.geometry;
                            vm.parcel.properties = result.feature.properties && result.feature.properties.hasOwnProperty('html') ? result.feature.properties.html : [];
                            vm.parcel.area = result.feature.properties && result.feature.properties.hasOwnProperty('area') ? result.feature.properties.area : 0;
                            vm.parcel.plan_id = result.feature.properties && result.feature.properties.hasOwnProperty('plan_id') ? result.feature.properties.plan_id : null;
                            vm.parcel.plan_info = [];
                            vm.parcel.show_saved_feature = result.hasOwnProperty('show_saved_feature') ? true : false;
                            
                            if(vm.parcel.properties.length){
                                vm.parcel.is_show = true;
                            }

                            vm.drawParcel({
                                type: 'Feature',
                                geometry: vm.parcel.geometry
                            }, true);

                            if(result.feature.geometry.type == 'Polygon'){
                                if(vm.parcel.properties.length == 0){
                                    vm.getProperties(vm.parcel).then(()=>{
                                        vm.checkPlan();
                                    });
                                }else{
                                    vm.checkPlan();
                                }
                            }else{
                                if(result.feature.geometry.type == 'Point'){
                                    vm.checkPlan();
                                }
                            }
                        }
                    }
                });
            },
            hideSelectedParcel: function(){
                this.parcel.is_show = false;
                if(this.parcel.layer){
                    this.parcel.layer.remove();
                    this.parcel.layer = null;
                    this.parcel.geometry = null;
                    this.parcel.properties = [];
                }
            },
            openDocumentURL: function(e){
                let vm = this;
                vm.$root.postData(vm.$root.setting.api_resource.document, {
                    ward_id: vm.ward.id,
                    level: vm.ward.level
                }).then(res => {
                    if(res.error){
                        vm.$root.showMessageBox(res.message);
                    }else{
                        vm.$root.openLink(res.data);
                    }
                });
            },
            selectLayer: function(e, selected){
                let vm = this;
                e.target.closest('div.layer-items').style.display = "none";
                setTimeout(()=>{
                    e.target.closest('div.layer-items').style.removeProperty('display');
                }, 200);

                /** Kiểm tra loại bản đồ không có tọa độ trục */
                if(selected && selected.hasOwnProperty('map_type') && selected.map_type == 'simple'){
                    vm.loadSimpleMap(selected);
                }else{
                    vm.selected_layer_id = selected.id;
                    vm.reloadLayer();
                    vm.checkPlan();
                }
            },
            openColorList: function(e){
                this.$root.$refs.colorlist.open();
            },
            toggleRuler: function(e){
                if(this.is_draw_ruler){
                    this.is_draw_ruler = false;
                    this.ruler.features = [];
                    this.ruler.drawing_feature = null;
                    this.drawRuler();
                }else{
                    this.is_draw_ruler = true;
                }
            },
            checkPlan: function(){
                let vm = this;
                vm.parcel.plan_info = [];
                vm.parcel.plan_detail = [];
                if(vm.parcel.layer){
                    let parcelFeature = vm.parcel.layer.toGeoJSON().features[0];
                    
                    if(parcelFeature.geometry.type == "Polygon"){
                        parcelFeature.properties = {area: vm.parcel.area};
                    }

                    if(parcelFeature.geometry.type == "Point" || parcelFeature.geometry.type == "Polygon"){
                        vm.$root.postData(vm.$root.setting.api_resource.checkplan, {
                            feature: parcelFeature,
                            layer_id: vm.selected_layer_id
                        }).then(result => {
                            vm.parcel.is_checking_plan = false;
                            if(result.error == false){
                                vm.parcel.is_show = true;
                                vm.parcel.plan_info = result.plan;
                                vm.parcel.plan_detail = typeof result.detail != 'undefined' ? result.detail : [];
                            }
                        });   
                    }
                }
            },
            findPolygon: function(point){
                let vm = this;
                if(vm.ward){
                    vm.$refs['province-box'].$el.classList.add('hide');
                    vm.resetParcel();

                    if(window.timeout_find_polygon){
                        clearTimeout(window.timeout_find_polygon);
                    }

                    window.timeout_find_polygon = setTimeout(()=>{
                        vm.is_finding = true;
                        vm.$root.postData(vm.$root.setting.api_resource.polygon, {
                            point: {
                                lng: point.lng,
                                lat: point.lat
                            },
                            app_version: 3,
                            ward_id: vm.ward.id
                        }).then(res => {
                            vm.is_finding = false;
                            if(!res.error){
                                vm.parcel.geometry = JSON.parse(res.data.geometry);
                                vm.parcel.properties = res.data.properties;
                                vm.parcel.is_show = true;
                                vm.parcel.plan_id = res.data.parcel && res.data.parcel.hasOwnProperty('plan_id') ? res.data.parcel.plan_id : null;
                                vm.parcel.base_coordinate = res.data.parcel && res.data.parcel.hasOwnProperty('base_coordinate') ? res.data.parcel.base_coordinate : 0;
                                vm.parcel.area = res.data.parcel && res.data.parcel.hasOwnProperty('area') ? res.data.parcel.area : 0;
                                vm.drawParcel({
                                    type: 'Feature',
                                    geometry: vm.parcel.geometry
                                }, true);
                                vm.checkPlan();
                            }else{
                                vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                                    lng: point.lng,
                                    lat: point.lat
                                }).then((res)=>{
                                    if(!res.error && res.data){
                                        vm.parcel.geometry = {
                                            type: 'Point',
                                            coordinates: [point.lng, point.lat]
                                        };

                                        vm.parcel.properties = res.data.html;
                                        vm.parcel.is_show = true;
                                        vm.parcel.plan_id = null;

                                        vm.drawParcel({
                                            type: 'Feature',
                                            geometry: vm.parcel.geometry
                                        }, true);

                                        vm.checkPlan();
                                    }
                                });
                            }
                        });
                    }, 300)
                }
            },
            drawParcel: function(feature, mustMove){
                let vm = this;
                let move = true;
                if(vm.parcel.layer){
                    vm.parcel.layer.remove();
                    move = false;
                }

                if(mustMove){
                    move = true;
                }

                if(feature){
                    vm.parcel.layer = L.geoJSON(feature, {
                        style: function (feature) {
                            return {
                                weight: 2,
                                fill: true,
                                fillOpacity: 0.2
                            };
                        }
                    }).addTo(vm.map);

                    vm.parcel.layer.showMeasurements({
                        showDistances: vm.parcel.show_distance,
                        showArea: false,
                        showTotalDistance: false,
                    });

                    if(move){
                        function targetPoint(latlng, dx, dy) {
                            // dx, dy theo mét
                            let R = 6378137; // bán kính trái đất (m)
                            let newLat = latlng.lat + (dy / R) * (180 / Math.PI);
                            let newLng = latlng.lng + (dx / (R * Math.cos(Math.PI * latlng.lat / 180))) * (180 / Math.PI);
                            return L.latLng(newLat, newLng);
                        }

                        // Lấy bounds và tâm polygon
                        let bounds = vm.parcel.layer.getBounds();
                        let center = bounds.getCenter();
                        let zoom = vm.map.getBoundsZoom(bounds);
                        
                        let target = targetPoint(center, 0, vm.getTargetByZoom(zoom));

                        if(window.getFeatureArea(feature.geometry) > 500){
                            zoom = zoom - 1;
                        }

                        zoom = zoom > 20 ? 20 : zoom;

                        vm.map.setView(target, zoom, {
                            animate: true,
                            maxZoom: 20
                        });
                    }
                }
            },
            getTargetByZoom: function(zoom){
                switch (zoom) {
                    case 20:
                        return -30;
                        break;
                    case 19:
                        return -70;
                        break;
                    case 18:
                        return -130;
                        break;
                    case 17:
                        return -250;
                        break;
                    case 16:
                        return -350;
                        break;
                    default:
                        return 0;
                        break;
                }
            },
            changeMapType: function(type){
                if(this.maptype != type){
                    this.maptype = type;
                    this.reloadLayer();
                }
            },
            loadSimpleMap: function(layer){
                let vm = this;
                vm.$root.$refs.simplemap.open({
                    layer: layer
                });
            },
            reloadLayer: function(){
                let vm = this;
                /** Kiểm tra loại bản đồ không có tọa độ trục */
                if(vm.current_layer && vm.current_layer.hasOwnProperty('map_type') && vm.current_layer.map_type == 'simple'){
                    vm.loadSimpleMap(vm.current_layer);
                    return;
                }

                /** Tạo lại map và clear trắng map nếu có layers */
                vm.createMaps({
                    center: {
                        lng: vm.feature ? vm.feature.center.coordinates[0] : vm.map.getCenter().lng,
                        lat: vm.feature ? vm.feature.center.coordinates[1] : vm.map.getCenter().lat
                    }
                }).then(()=>{
                    /** Thêm các layer đang chọn vào map */ 
                    vm.layers = [];
                    if(vm.current_layer && vm.current_layer.config){
                        for (let index = 0; index < vm.current_layer.config.length; index++) {
                            const element = vm.current_layer.config[index];
                            vm.layers.push(L.tileLayer.vn2000(element.url,{
                                tileSize: element.hasOwnProperty('tileSize') ? element.tileSize : 256,
                                opacity: element.opacity,
                                minZoom: element.minZoom,
                                maxZoom: element.maxZoom,
                                attribution: "",
                                zoomOffset: element.hasOwnProperty('zoomOffset') ? element.zoomOffset : 0
                            }).addTo(vm.map));

                            vm.layers[vm.layers.length - 1].setOpacity(vm.opacity / 10);
                        }
                    }
                    
                    /** Thêm polygon khu vực đang chọn */
                    vm.addBoundaryPolygon();

                    /** Thêm thửa đang chọn */
                    if(vm.parcel.layer){
                        vm.drawParcel(vm.parcel.layer.toGeoJSON());
                    }

                    if(typeof window.callbackAfterInitMap == 'function'){
                        window.callbackAfterInitMap();
                        window.callbackAfterInitMap = null;
                    }

                    /** Vẽ vị trí điểm hiện tại */
                    vm.drawMyLocation();

                    /** Thêm các điểm dự án (nếu có) vào bản đồ */
                    vm.addObjectLayerPoint();
                });

                if(vm.is_draw_ruler){
                    vm.drawRuler();
                }
            },
            addObjectLayerPoint: function(){
                let vm = this;
                if(vm.object_layers.length > 0){
                    vm.layers.push(L.geoJSON(vm.object_layers, {
                        filter: function (feature) {
                            return feature.properties.length > 0;
                        },
                        onEachFeature: function (feature, layer) {
                            layer.on('click', function (e) {
                                let properties_html = feature.properties.map((item)=>{
                                    item = item.split(': ');
                                    return `<div class="row-object-layer">
                                        <div class="label">${item[0]}</div>
                                        <div class="value">${item[1]}</div>
                                        </div>`;
                                }).join('');

                                vm.$root.$refs.marker_info[0].open({
                                    properties_html: properties_html
                                });
                            });
                        }
                    }).addTo(vm.map));
                }
            },
            addPoint: function(element){
                let vm = this;
                let properties_html = element.config.hasOwnProperty('properties_html') ? element.config.properties_html : [];
                properties_html = properties_html.map((item)=>{
                    item = item.split(': ');
                    return `<div class="row">
                        <div class="label">${item[0]}</div>
                        <div class="value">${item[1]}</div>
                        </div>`;
                }).join('');

                let myIcon = L.divIcon({
                    className: 'marker-pin-icon',
                    html: `<div class="marker-item">${element.name}</div>`
                });

                let marker = L.marker(element.geometry.coordinates, {
                    properties_html: properties_html
                });
                
                marker.addTo(this.map);

                marker.on('click', (e)=> {
                    if(e.target.options.properties_html != ''){
                        vm.$root.$refs.marker_info[0].open({
                            properties_html: e.target.options.properties_html
                        });
                    }
                });

                vm.layers.push(marker);
            },
            drawRuler: function(endpoint){
                let vm = this;

                // Xóa các layer đang hiển thị trước đó;
                vm.ruler.layers.forEach(element => {
                    element.remove();
                });

                vm.ruler.layer_points.forEach(element => {
                    element.remove();
                });

                vm.ruler.layers = [];

                // Vẽ các layer đã ngắt vùng
                vm.ruler.features.forEach((feature)=>{
                    let newFeatures = {
                        type: "FeatureCollection",
                        features: [feature]
                    };

                    let points = feature.geometry.type == 'Polygon' ? feature.geometry.coordinates[0] : [];
                    points = feature.geometry.type == 'LineString' ? feature.geometry.coordinates : points;

                    for (let index = 0; index < points.length; index++) {
                        const point = points[index];
                        newFeatures.features.push({
                            type: 'Feature',
                            geometry: {
                                type: 'Point',
                                coordinates: point
                            }
                        });
                    }

                    let layer = L.geoJSON(newFeatures, {
                        style: function (f) {
                            return {
                                weight: 1,
                                stroke: 1
                            };
                        },
                        pointToLayer: function (feature, latlng) {
                            return L.circleMarker(latlng, {
                                radius: 3,
                                fillColor: '#007bff',
                                color: '#fff',
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 0.8
                            });
                        }
                    }).addTo(vm.map).showMeasurements({
                        showDistances: vm.ruler.show_distance,
                        showArea: false,
                        showTotalDistance: false,
                    });

                    vm.ruler.layers.push(layer);

                });
                
                // Vẽ layer đang chọn
                if(vm.ruler.drawing_feature){
                    let feature = JSON.parse(JSON.stringify(vm.ruler.drawing_feature));
                    if(feature.geometry.type == "LineString" && endpoint){
                        feature.geometry.coordinates.push([endpoint.lng, endpoint.lat]);
                    }

                    let newFeatures = {
                        type: "FeatureCollection",
                        features: [feature]
                    };

                    let points = feature.geometry.coordinates;

                    for (let index = 0; index < points.length - 1; index++) {
                        const point = points[index];
                        newFeatures.features.push({
                            type: 'Feature',
                            geometry: {
                                type: 'Point',
                                coordinates: point
                            }
                        });
                    }

                    let layer = L.geoJSON(newFeatures, {
                        style: function (feature) {
                            // Chỉ áp dụng cho LineString / Polygon
                            if (feature.geometry.type !== 'Point' && feature.geometry.type !== 'MultiPoint') {
                                return {
                                    weight: 1,
                                    dashArray: '3, 3', 
                                    dashOffset: '2',
                                    stroke: 1
                                };
                            }

                            return {
                                weight: 1,
                                stroke: 1
                            };
                        },
                        pointToLayer: function (feature, latlng) {
                            return L.circleMarker(latlng, {
                                radius: 3,
                                fillColor: '#007bff',
                                color: '#fff',
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 0.8
                            });
                        }
                    }).addTo(vm.map).showMeasurements({
                        showDistances: vm.ruler.show_distance,
                        showArea: false,
                        showTotalDistance: false,
                    });

                    vm.ruler.layers.push(layer);
                }
            },
            drawMyLocation: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    if(vm.my_location.point && !vm.my_location.layer){
                        var myIcon = L.divIcon({
                            className: 'marker-wrap',
                            html: '<div class="current-marker-item"></div>'
                        });

                        vm.my_location.layer = L.marker([vm.my_location.point.lat, vm.my_location.point.lng], {icon: myIcon}).addTo(vm.map);

                        let current_zoom = vm.map.getZoom() > 16 ? vm.map.getZoom() : 18;
                        vm.map.setView([vm.my_location.point.lat, vm.my_location.point.lng], current_zoom);
                    }else if(vm.my_location.layer){
                        vm.my_location.layer.addTo(vm.map);
                        vm.my_location.layer.setLatLng([vm.my_location.point.lat, vm.my_location.point.lng]);
                    }
                    resolve();
                });
            },
            changeBoundaryStyle: function(zoom){
                if(this.boundaryPolygon){
                    if(zoom < 15){
                        this.boundaryPolygon.setStyle({
                            weight: 3,
                            dashArray: null,
                            dashOffset: null
                        });
                    }else{
                        this.boundaryPolygon.setStyle({
                            weight: 1,
                            dashArray: '3 3',
                            dashOffset: '1'
                        });
                    }
                }
            },
            addBoundaryPolygon: function(){
                let vm = this;
                if(vm.feature){
                    if(!vm.boundaryPolygon){
                        vm.map.setView({
                            lng: vm.feature ? vm.feature.center.coordinates[0] : vm.map.getCenter().lng,
                            lat: vm.feature ? vm.feature.center.coordinates[1] : vm.map.getCenter().lat
                        }, vm.map.getZoom());
                    }

                    vm.boundaryPolygon = L.geoJSON({
                        type: 'Feature',
                        geometry: vm.feature.geom
                    }, {
                        style: function (feature) {
                            return {
                                weight: 3,
                                fill: false,
                                dashArray: '3 3',
                                dashOffset: '1'
                            };
                        }
                    }).addTo(vm.map);
                }
            },
            createMaps: function(option){
                let vm = this;
                return new Promise(function(resolve, reject){
                    let center = [option.center.lat, option.center.lng];
                    let defaultZoom = vm.map ? vm.map.getZoom() : 14;

                    if(vm.map){
                        vm.map.eachLayer(function (layer) {
                            vm.map.removeLayer(layer)
                        });
                        vm.map.options.maxZoom = option.map_max_zoom && option.map_max_zoom > 0 ? option.map_max_zoom : 22;
                    }else{
                        vm.map = new L.map(vm.$refs.gmap,{ 
                            minZoom: 10,
                            maxZoom: option.map_max_zoom && option.map_max_zoom > 0 ? option.map_max_zoom : 22,
                            zoomControl: false,
                            attributionControl: false
                        }).setView(center, defaultZoom);
                    }

                    let mapKeyUsage = vm.$root.setting.maps_usage;
                    let mapUsage = vm.$root.setting.maps_api[mapKeyUsage][vm.maptype];

                    if(typeof L.tileLayer.vn2000 != 'undefined'){
                        vm.layers.push(L.tileLayer.vn2000(mapUsage.url, mapUsage.config).addTo(vm.map));
                    }else{
                        vm.$root.showMessageBox('Kết nối mạng của bạn quá chậm không thể tải được bản đồ vui lòng thử kết nối mạng khác, tắt ứng dụng và thử lại.');
                    }

                    vm.map.on('click', function(e) {
                        if(vm.$root.u){
                            /** Đang trong chế độ vẽ thì thêm điểm */
                            if(vm.is_draw_ruler){
                                vm.$refs.ruler_box.addPoint(e.latlng);
                            }else{
                                if(vm.ward){
                                    vm.findPolygon(e.latlng, 'direct');
                                }else{
                                    vm.showAbsolutePoint({
                                        type: 'Feature',
                                        geometry: {
                                            type: 'Point',
                                            coordinates: [e.latlng.lng, e.latlng.lat]
                                        }
                                    });
                                }
                            }
                        }else{
                            vm.showAbsolutePoint({
                                type: 'Feature',
                                geometry: {
                                    type: 'Point',
                                    coordinates: [e.latlng.lng, e.latlng.lat]
                                }
                            });
                        }
                    });

                    vm.map.on('zoom', function(e){

                        /* Thay đổi style nét vẽ đứt hoặc liền theo độ zoom */
                        vm.changeBoundaryStyle(vm.map.getZoom());
                    });

                    vm.map.on('mousemove', function(e){
                        if(vm.$root.u){
                            if(vm.is_draw_ruler){
                                vm.drawRuler(e.latlng);
                            }
                        }
                    });

                    vm.map.on('moveend', function(e){
                        if(vm.$root.u){
                            vm.loadParcelLabel();
                            vm.loadSavedFeatures();
                        }
                    });

                    vm.map.on('contextmenu', function(e){
                        if(vm.$root.u){
                            if(vm.is_draw_ruler){
                                vm.$root.showConfirmBox({
                                    message: 'Bạn có muốn khoanh vùng cho điểm đo này ?',
                                    callback: function(confirm){
                                        if(confirm){
                                            vm.$refs.ruler_box.endDrawPolygon();
                                        }else{
                                            vm.$refs.ruler_box.cutPoint();
                                        }
                                    }
                                })
                            }
                        }
                    });

                    resolve(true);
                });
            },
            drawParcelLabel: function(features){
                var geodata = {
                    "type": "FeatureCollection",
                    "features": features
                };

                if(window.parcelLabelLayer){
                    window.parcelLabelLayer.remove();
                }

                window.parcelLabelLayer = L.vectorGrid.slicer(geodata, {
                    rendererFactory: L.canvas.tile,
                    vectorTileLayerStyles: {
                        sliced: function() {
                            return [
                                {
                                    color: '#ffffff',
                                    weight: 3,
                                    opacity: 1
                                },
                                {
                                    color: '#333',
                                    weight: 1,
                                    opacity: 1
                                }
                            ];
                        }
                    },
                    maxZoom: 20
                }).addTo(this.map);

                window.parcelLabelFeatures = features;
            },
            loadParcelLabel: function(){
                let vm = this;

                if(vm.map.getZoom() < 19){
                    vm.clearParcelLabel();
                }

                if (typeof Worker !== 'undefined') {
                    if(typeof window.myWorker == 'undefined'){
                        window.myWorker = new Worker('/assets/web-v1/js/worker/load-parcel-label.js?t=' + (new Date()).getTime());
                        window.myWorker.onmessage = function(e) {
                            if(window.parcelLabelFeatures){
                                let bounds = vm.map.getBounds();
                                let features = window.parcelLabelFeatures.filter((f)=>{
                                    let layer = L.geoJSON(f);
                                    return bounds.intersects(layer.getBounds());
                                });
                                e.data.features = window.uniqueFeatures(e.data.features.concat(features));
                            }

                            vm.drawParcelLabel(e.data.features);
                        }
                    }
                }
                
                if(vm.parcel.show_parcel_label && vm.parcel.layer){
                    if(window.parcelLabelTimeout){
                        clearTimeout(window.parcelLabelTimeout);
                    }

                    window.parcelLabelTimeout = setTimeout(()=>{
                        let zoom = vm.map.getZoom();
                        if(zoom >= 19){
                            let center = vm.map.getCenter();
                            vm.$root.postData(vm.$root.setting.api_resource.parcel_label, {
                                center: {
                                    lng: center.lng,
                                    lat: center.lat
                                },
                                bbox: vm.getBBoxGeometry()
                            }).then(res => {
                                if(!res.error){
                                    if(window.myWorker){
                                        window.myWorker.postMessage({
                                            features: res.data,
                                            zoom: zoom
                                        });
                                    }
                                }
                            });
                        }
                    }, 1000)
                }else{
                    vm.clearParcelLabel();
                }
            },
            clearParcelLabel: function(){
                if(window.parcelLabelLayer){
                    window.parcelLabelLayer.remove();
                    window.parcelLabelLayer = null;
                }
            },
            loadSavedFeatures: function(){
                let vm = this;
                if(vm.parcel.show_saved_feature){
                    if(window.savedFeatureTimeout){
                        clearTimeout(window.savedFeatureTimeout);
                    }

                    window.savedFeatureTimeout = setTimeout(()=>{
                        vm.$root.postData(vm.$root.setting.api_resource.saved_features, {
                            bbox: vm.getBBoxGeometry()
                        }).then(res => {
                            if(!res.error){
                                let newFeatures = res.data.map((f)=>{
                                    return {
                                        type: 'Feature',
                                        geometry: vm.$root.getItemGeometry(f),
                                        properties: {
                                            center: JSON.parse(f.center),
                                            name: f.name,
                                            note: f.note
                                        }
                                    };
                                });

                                if(window.savedFeatureList){
                                    let bounds = vm.map.getBounds();
                                    let features = window.savedFeatureList.filter((f)=>{
                                        let layer = L.geoJSON(f);
                                        return bounds.intersects(layer.getBounds());
                                    });

                                    newFeatures = window.uniqueFeatures(newFeatures.concat(features));
                                }

                                vm.drawSavedFeatures(newFeatures);
                            }
                        });
                    }, 800)
                }else{
                    if(window.savedFeatureLayer){
                        window.savedFeatureLayer.remove();
                    }

                    if(window.savedFeatureLayer){
                        window.savedFeatureMarkerLayer.remove();
                    }
                }
            },
            drawSavedFeatures: function(features){
                /** Vẽ danh sách các thửa đã lưu */
                if(window.savedFeatureLayer){
                    window.savedFeatureLayer.remove();
                }

                window.savedFeatureLayer = L.geoJSON({
                        "type": "FeatureCollection",
                        "features": features.filter((f)=>{
                            return f.geometry.type != 'Point';
                        })
                    }, {
                    style: function (f) {
                        return {
                            weight: 2,
                            fill: false,
                            dashArray: '3 3',
                            dashOffset: '1'
                        };
                    }
                }).addTo(this.map);

                /** Hiển thị chiều dài cạnh */
                window.savedFeatureLayer.showMeasurements({
                    showDistances: this.map.getZoom() >= 18,
                    showArea: false
                });

                /** Vẽ danh sách các marker ghi chú tên thửa đã lưu */
                if(window.savedFeatureMarkerLayer){
                    window.savedFeatureMarkerLayer.remove();
                }

                window.savedFeatureMarkerLayer = L.geoJSON({
                        "type": "FeatureCollection",
                        "features": features.map((f)=>{
                            return {
                                type: 'Feature',
                                geometry: f.properties.center,
                                properties: {
                                    name: f.properties.name,
                                    note: f.properties.note
                                }
                            }
                        })
                    }, {
                    pointToLayer: function (feature, latlng) {
                        return L.marker(latlng, {
                            icon: L.divIcon({
                                className: "saved-marker-icon",
                                html: `
                                    <div class="point-body">
                                        <div class="point-label">${feature.properties.name}</div>
                                        <div class="point-description">${feature.properties.note}</div>
                                    </div>
                                `,
                                iconSize: [50, 50],
                                iconAnchor: [25, 25]
                            })
                        });
                    }
                }).addTo(this.map);

                window.savedFeatureList = features;
            },
            getProperties: function(feature){
                let vm = this;
                return new Promise((resolve)=>{
                    let centerPoint = vm.$root.getCenterGeometry(feature.geometry);
                    if(feature.geometry.type == "Polygon"){
                        // Lấy properties theo kiểu click polygon rồi so sánh trùng polygon với thửa đang click
                        vm.$root.postData(vm.$root.setting.api_resource.polygon, {
                            point: {
                                lng: centerPoint.lng,
                                lat: centerPoint.lat
                            },
                            ward_id: vm.ward.id
                        }).then(res => {
                            if(!res.error){
                                let parcelCenter = vm.$root.getCenterGeometry(JSON.parse(res.data.geometry));
                                let distance = centerPoint.distanceTo(parcelCenter);
                                let compairArea = Math.abs(window.getFeatureArea(JSON.parse(res.data.geometry)) - window.getFeatureArea(feature.geometry));
                                // So sánh diện tích thửa và khoảng cách giữa 2 điểm trung tâm thửa nếu không có chênh lệch thì thửa vẽ và thửa click là trùng 1 thửa
                                if(compairArea < 1 && distance < 1){
                                    vm.parcel.geometry = JSON.parse(res.data.geometry);
                                    vm.parcel.properties = res.data.properties;
                                    vm.parcel.is_show = true;
                                    vm.parcel.plan_id = res.data.parcel.plan_id;
                                    vm.parcel.base_coordinate = res.data.parcel.base_coordinate;
                                    resolve();
                                }else{
                                    // Lấy properties theo tọa độ trung tâm thửa
                                    vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                                        lng: centerPoint.lng,
                                        lat: centerPoint.lat
                                    }).then((res)=>{
                                        if(!res.error && res.data){
                                            let featureArea = window.getFeatureArea(feature.geometry);
                                            res.data.html.push(`<div class="label">Diện tích</div><div class="value">${featureArea.toFixed(1)} m<sup>2</sup></div>`);
                                            vm.parcel.properties = res.data.html;
                                            vm.parcel.is_show = true;
                                            vm.parcel.plan_id = null;
                                            resolve();
                                        }
                                    });
                                }
                            }else{
                                // Lấy properties theo tọa độ trung tâm thửa
                                vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                                    lng: centerPoint.lng,
                                    lat: centerPoint.lat
                                }).then((res)=>{
                                    if(!res.error && res.data){
                                        let featureArea = window.getFeatureArea(feature.geometry);
                                        res.data.html.push(`<div class="label">Diện tích</div><div class="value">${featureArea.toFixed(1)} m<sup>2</sup></div>`);
                                        vm.parcel.properties = res.data.html;
                                        vm.parcel.is_show = true;
                                        vm.parcel.plan_id = null;
                                        resolve();
                                    }
                                });
                            }
                        });
                    }else{
                        // Lấy properties theo tọa độ trung tâm thửa
                        vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                            lng: centerPoint.lng,
                            lat: centerPoint.lat
                        }).then((res)=>{
                            if(!res.error && res.data){
                                vm.parcel.properties = res.data.html;
                                vm.parcel.is_show = true;
                                vm.parcel.plan_id = null;
                                resolve();
                            }
                        });
                    }
                })
            },
            getBBoxGeometry: function(){
                let bounds = this.map.getBounds();
                return {
                    "type": "Polygon",
                    "coordinates": [[
                        [bounds.getWest(), bounds.getSouth()],
                        [bounds.getEast(), bounds.getSouth()],
                        [bounds.getEast(), bounds.getNorth()],
                        [bounds.getWest(), bounds.getNorth()],
                        [bounds.getWest(), bounds.getSouth()]
                    ]]
                }
            }
        },
        computed: {
            current_layer: function(){
                let selected = this.option_layers.filter((layer)=>{
                    return layer.id == this.selected_layer_id;
                });
                return selected.length > 0 ? selected[0] : null;
            }
        },
        watch: {
            'opacity': function(){
                this.changeLayerOpacity();
            },
            'parcel.show_distance': function(){
                this.reloadLayer();
            },
            'parcel.show_parcel_label': function(){
                this.loadParcelLabel();
            },
            'ruler.show_distance': function(){
                this.reloadLayer();
            },
            'is_draw_ruler': function(newval){
                this.drawRuler();
            },
            'parcel.show_saved_feature': function(){
                this.loadSavedFeatures();
            }
        }
    });

    Vue.component('simplemap', {
        template: `
        <div class="modal">
            <div class="modal-body simplemap animate">
                <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="modal-title">{{ layer ? layer.name : '' }}</div>
                <div class="staticmap">
                    <div ref="gmap" class="gmap simplemap" style="background: url('/assets/web-v1/images/bandogiay-bg.jpg') repeat !important"></div>
                </div>
            </div>
        </div>
        `,
        data: function(){
            return {
                map: null,
                layer: null,
                southWest: {
                    11: [4, 4],
                    12: [8, 8],
                    13: [16, 17],
                    14: [33, 35],
                    15: [67, 71],
                    16: [135, 142],
                    17: [270, 284]
                }
            }
        },
        methods: {
            createMap: function(){
                let vm = this;
                return new Promise(function(resolve, reject){
                    if(vm.map){
                        vm.map.remove();
                    }

                    vm.map = new L.map(vm.$refs.gmap,{ 
                        minZoom: 11,
                        maxZoom: 17,
                        zoomControl: false,
                        attributionControl: false,
                        renderer: L.svg(),
                        crs: L.CRS.Simple
                    });

                    for (let index = 0; index < vm.layer.config.length; index++) {
                        const element = vm.layer.config[index];
                        L.tileLayer.vn2000(element.url, {
                            tileSize: element.hasOwnProperty('tileSize') ? element.tileSize : 256,
                            opacity: element.opacity,
                            minZoom: element.minZoom,
                            maxZoom: element.maxZoom,
                            zoomOffset: element.hasOwnProperty('zoomOffset') ? element.zoomOffset : 0
                        }).addTo(vm.map);
                    }
                    
                    resolve(true);
                });
            },
            setCenterMap: function(e){
                const t = (256 * (e[1] + 1) - window.innerHeight) / 2;
                var a = 256 * (e[0] + 1) / 2
                    , i = this.map.unproject([0, 256 * (e[1] + 1) / 2 - t], this.map.getMinZoom() - 1)
                    , o = this.map.unproject([a, 0], this.map.getMinZoom() - 1);
                return new L.LatLngBounds(i,o);
            },
            open: function(option){
                this.layer = option && typeof option.layer!='undefined' ? option.layer : null;
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');

                this.createMap().then(()=>{
                    let o = this.setCenterMap(this.southWest[11]);
                    this.map.fitBounds(o);
                });
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        mounted: function(){
            
        }
    });

    Vue.component('ruler-box', {
        props: ["ruler"],
        template: ` 
            <div class="ruler-box">
                <div class="ruler-controller" ref="ruler_box">
                    <div class="close-btn" @click.stop.prevent="close($event)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <template v-if="ruler.features.length > 0">
                        <div class="title">Thông tin điểm đo</div>
                        <div class="items">
                            <template v-for="(item, index) in ruler.features">
                                <div class="item">
                                    <span class="name">{{ item.properties.name }}</span>
                                    <span class="area">{{ item.properties.area }} m<sup>2</sup></span>
                                    <div class="action-icons">
                                        <span class="polygon-icon" title="Bảng tọa độ ranh thửa" @click.stop.prevent="viewCoordinate(item)"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="draw-square" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" class="svg-inline--fa fa-draw-square fa-w-14 fa-3x"><path fill="currentColor" d="M400 354.26V157.74c27.56-7.14 48-31.95 48-61.74 0-35.35-28.65-64-64-64-29.79 0-54.6 20.45-61.74 48H125.74C118.6 52.45 93.79 32 64 32 28.65 32 0 60.65 0 96c0 29.79 20.44 54.6 48 61.74v196.53C20.44 361.4 0 386.21 0 416c0 35.35 28.65 64 64 64 29.79 0 54.6-20.44 61.74-48h196.53c7.14 27.56 31.95 48 61.74 48 35.35 0 64-28.65 64-64-.01-29.79-20.45-54.6-48.01-61.74zM322.26 400H125.74c-5.8-22.41-23.32-39.93-45.74-45.74V157.74c22.41-5.8 39.93-23.32 45.74-45.74h196.53c5.8 22.41 23.32 39.93 45.74 45.74v196.53c-22.42 5.8-39.94 23.32-45.75 45.73zM384 64c17.64 0 32 14.36 32 32s-14.36 32-32 32-32-14.36-32-32 14.36-32 32-32zM32 96c0-17.64 14.36-32 32-32s32 14.36 32 32-14.36 32-32 32-32-14.36-32-32zm32 352c-17.64 0-32-14.36-32-32s14.36-32 32-32 32 14.36 32 32-14.36 32-32 32zm320 0c-17.64 0-32-14.36-32-32s14.36-32 32-32 32 14.36 32 32-14.36 32-32 32z"></path></svg></span>
                                        <span class="save-icon" title="Lưu vùng đo" @click.stop.prevent="saveFeature(item)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M433.1 129.1l-83.9-83.9C342.3 38.32 327.1 32 316.1 32H64C28.65 32 0 60.65 0 96v320c0 35.35 28.65 64 64 64h320c35.35 0 64-28.65 64-64V163.9C448 152.9 441.7 137.7 433.1 129.1zM224 416c-35.34 0-64-28.66-64-64s28.66-64 64-64s64 28.66 64 64S259.3 416 224 416zM320 208C320 216.8 312.8 224 304 224h-224C71.16 224 64 216.8 64 208v-96C64 103.2 71.16 96 80 96h224C312.8 96 320 103.2 320 112V208z"></path></svg></span>
                                        <span class="qr-icon" title="Mã chia sẻ vùng đo" @click.stop.prevent="createShareCode(item)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M40 32C53.25 32 64 42.75 64 56V456C64 469.3 53.25 480 40 480H24C10.75 480 0 469.3 0 456V56C0 42.75 10.75 32 24 32H40zM128 48V464C128 472.8 120.8 480 112 480C103.2 480 96 472.8 96 464V48C96 39.16 103.2 32 112 32C120.8 32 128 39.16 128 48zM200 32C213.3 32 224 42.75 224 56V456C224 469.3 213.3 480 200 480H184C170.7 480 160 469.3 160 456V56C160 42.75 170.7 32 184 32H200zM296 32C309.3 32 320 42.75 320 56V456C320 469.3 309.3 480 296 480H280C266.7 480 256 469.3 256 456V56C256 42.75 266.7 32 280 32H296zM448 56C448 42.75 458.7 32 472 32H488C501.3 32 512 42.75 512 56V456C512 469.3 501.3 480 488 480H472C458.7 480 448 469.3 448 456V56zM384 48C384 39.16 391.2 32 400 32C408.8 32 416 39.16 416 48V464C416 472.8 408.8 480 400 480C391.2 480 384 472.8 384 464V48z"></path></svg></span>
                                        <span class="trash-icon" title="Xóa vùng đo" @click.stop.prevent="removeFeature(index)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M135.2 17.69C140.6 6.848 151.7 0 163.8 0H284.2C296.3 0 307.4 6.848 312.8 17.69L320 32H416C433.7 32 448 46.33 448 64C448 81.67 433.7 96 416 96H32C14.33 96 0 81.67 0 64C0 46.33 14.33 32 32 32H128L135.2 17.69zM394.8 466.1C393.2 492.3 372.3 512 346.9 512H101.1C75.75 512 54.77 492.3 53.19 466.1L31.1 128H416L394.8 466.1z"/></svg></span>
                                    </div>
                                </div>
                            </template>
                        </div>
                        <label class="checkbox mb-1 mt-1">
                            <input type="checkbox" v-model="ruler.show_distance" />
                            <span>Ẩn / hiện chiều dài cạnh (điểm đo)</span>
                        </label>
                    </template>
                    <template v-else>
                        <div class="title">Hướng dẫn</div>
                        <div class="mb-1 description">Chế độ đo đang bật, nhấn chuột trái vào bản đồ để chọn điểm, nhấn chuột phải vào bản đồ để ngắt vùng đo sang vùng đo mới</div>
                    </template>
                </div>
            </div>
        `,
        methods: {
            close: function(e){
                this.ruler.features = [];
                this.ruler.drawing_feature = null;
                this.$parent.toggleRuler();
                this.$parent.drawRuler();
            },
            createShareCode: function(feature){
                let vm = this;
                vm.$root.postData(vm.$root.setting.api_resource.create_sharecode, {
                    geometry: feature.geometry
                }).then(res => {
                    if(res.error){
                        vm.$root.showMessageBox(res.message);
                    }else{
                        vm.$root.$refs.sharecode.open({
                            code: res.data.code,
                            expired: res.data.expired
                        });
                    }
                });
            },
            saveFeature: function(feature){
                let vm = this;
                vm.$root.$refs.newpoint.open({
                    form: {
                        name: '',
                        note: `${vm.$parent.ward.name}, ${vm.$parent.province.name}`,
                        geometry: feature.geometry
                    }
                });
            },
            viewCoordinate: function(feature){
                let mainProvince = this.$parent.province.hasOwnProperty('childs') ? this.$parent.province.childs.find(item => item.is_main) : this.$parent.province;
                if(mainProvince){
                    this.$root.reloadC(mainProvince.base_coordinate);
                    let points = feature.geometry.type == "Polygon" ? JSON.parse(JSON.stringify(feature.geometry.coordinates[0])) : JSON.parse(JSON.stringify(feature.geometry.coordinates));
                    points = points.map((point)=>{
                        let lng = point[0];
                        let lat = point[1];

                        let vn2000Point = this.$root.e(atob(this.$root.b),atob(this.$root.a)).inverse([lng, lat]);
                        return {
                            lng: Number(lng.toFixed(10)),
                            lat: Number(lat.toFixed(10)),
                            x: Number(vn2000Point[0].toFixed(3)),
                            y: Number(vn2000Point[1].toFixed(3))
                        };
                    });

                    this.$root.$refs.coordinatetable.open({
                        points: points,
                        base_coordinate: mainProvince.base_coordinate
                    });
                }
            },
            removeFeature: function(index){
                this.ruler.features.splice(index, 1);
                this.$parent.drawRuler();
            },
            addPoint: function(point){
                if(!this.ruler.drawing_feature){
                    this.ruler.drawing_feature = {
                        type: "Feature",
                        geometry: {
                            type: "LineString",
                            coordinates: [[point.lng, point.lat]]
                        }
                    }
                }else{
                    this.ruler.drawing_feature.geometry.coordinates.push([point.lng, point.lat]);
                }

                console.log(this.ruler.drawing_feature.geometry.coordinates);
                this.$parent.drawRuler();
            },
            endDrawPolygon: function(){
                let vm = this;
                if(vm.ruler.drawing_feature){
                    let feature = JSON.parse(JSON.stringify(vm.ruler.drawing_feature));
                    if(feature.geometry.coordinates.length > 2){
                        feature.geometry.coordinates.push(feature.geometry.coordinates[0]);
                        feature.geometry.type = "Polygon";
                        feature.geometry.coordinates = [feature.geometry.coordinates];
                        feature.properties = {
                            name: 'Vùng đo ' + (vm.ruler.features.length + 1),
                            area: window.getFeatureArea(feature.geometry).toFixed(1)
                        };

                        vm.ruler.features.push(feature);
                        vm.ruler.drawing_feature = null;
                        vm.$parent.drawRuler();
                    }else{
                        vm.$root.showMessageBox("Chức năng khoanh vùng chỉ hoạt đông khi có từ 3 điểm trở lên");
                    }
                }else{
                    vm.$root.showMessageBox("Chức năng khoanh vùng chỉ hoạt đông khi có từ 3 điểm trở lên");
                }
            },
            cutPoint: function(){
                let vm = this;
                if(vm.ruler.drawing_feature && vm.ruler.drawing_feature.geometry.coordinates.length > 1){
                    let feature = JSON.parse(JSON.stringify(vm.ruler.drawing_feature));
                    feature.properties = {
                        name: 'Vùng đo ' + (vm.ruler.features.length + 1),
                        area: 0
                    }

                    vm.ruler.features.push(feature);
                    vm.ruler.drawing_feature = null;
                }else{
                    vm.ruler.drawing_feature = null;
                }
                vm.$parent.drawRuler();
            },
        }
    });

    Vue.component('map-tools', {
        template: `
            <div class="map-tool" v-if="$parent.province && $parent.ward">
                <div class="item" @click.stop.prevent="openCityBox()">
                    <div class="selected-ward">
                        <div>{{ $parent.province.name }}</div>
                        <span class="split"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M96 480c-8.188 0-16.38-3.125-22.62-9.375c-12.5-12.5-12.5-32.75 0-45.25L242.8 256L73.38 86.63c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0l192 192c12.5 12.5 12.5 32.75 0 45.25l-192 192C112.4 476.9 104.2 480 96 480z"></path></svg></span>
                        <div>{{ $parent.ward.name }}</div>
                    </div>
                </div>
                <div class="item" @click.stop.prevent="$parent.openCheckParcel()">Kiểm tra sổ</div>
                <div class="item" @click.stop.prevent="$parent.toggleRuler()">
                    {{ $parent.is_draw_ruler ? 'Tắt' : 'Bật' }} thước đo
                    <div class="tooltip">
                        <div class="tooltip-title">Hướng dẫn đo</div>
                        <div>Nhấn chuột trái để chọn hoặc nối tiếp điểm. Nhấn chuột phải để ngắt điểm đo hiện tại và chuyển sang điểm đo mới.</div>
                    </div>
                </div>
                <div class="item" @click.stop.prevent="$parent.openColorList()">Chú giải</div>
                <div class="item" @click.stop.prevent="openCompass()">Xem hướng</div>
                <div class="item" @click.stop.prevent="$parent.openDocumentURL()">Quyết định</div>
                <div class="item layers" v-if="$parent.current_layer">
                    {{ $parent.current_layer.name }}
                    <span class="dropdown-icon"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path fill-rule="evenodd" clip-rule="evenodd" d="M12.7071 14.7071C12.3166 15.0976 11.6834 15.0976 11.2929 14.7071L6.29289 9.70711C5.90237 9.31658 5.90237 8.68342 6.29289 8.29289C6.68342 7.90237 7.31658 7.90237 7.70711 8.29289L12 12.5858L16.2929 8.29289C16.6834 7.90237 17.3166 7.90237 17.7071 8.29289C18.0976 8.68342 18.0976 9.31658 17.7071 9.70711L12.7071 14.7071Z"></path></g></svg></span>
                    <div class="layer-items">
                        <div v-for="item in $parent.option_layers" @click.stop.prevent="$parent.selectLayer($event, item)">{{ item.name }}</div>
                    </div>
                </div>
                <div class="item layer-opacity">
                    Làm mờ nền
                    <div class="rangeslider"><div class="mask-range" :style="'width:' + ($parent.opacity * 10) + '%'"></div> <input v-model="$parent.opacity" type="range" min="0" max="10"></div>
                </div>
            </div>
        `,
        methods: {
            openCityBox: function(){
                this.$parent.boundaryPolygon = null;
                this.$parent.parcel.is_show = false;
                this.$parent.$refs['province-box'].$el.classList.remove('hide');
            },
            openCompass: function(){
                this.$root.$refs.compass.open();
            }
        }
    });
    
    Vue.component('compass', {
        template: `
        <div class="compass">
            <div class="body-compass">
                <div class="close-btn" @click.stop.prevent="close($event)">
                    <span>Tắt la bàn</span>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--! Font Awesome Pro 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/></svg>
                </div>
                <div class="direction-items">
                    <div class="direction-name item-1">Bắc</div>
                    <div class="direction-name item-2">Đông Bắc</div>
                    <div class="direction-name item-3">Đông</div>
                    <div class="direction-name item-4">Đông Nam</div>
                    <div class="direction-name item-5">Nam</div>
                    <div class="direction-name item-6">Tây Nam</div>
                    <div class="direction-name item-7">Tây</div>
                    <div class="direction-name item-8">Tây Bắc</div>
                </div>
                <div class="mini-direction-items">
                    <div class="direction-name item-1">Khảm</div>
                    <div class="direction-name item-2">Cấn</div>
                    <div class="direction-name item-3">Chấn</div>
                    <div class="direction-name item-4">Tốn</div>
                    <div class="direction-name item-5">Ly</div>
                    <div class="direction-name item-6">Khôn</div>
                    <div class="direction-name item-7">Đoài</div>
                    <div class="direction-name item-8">Càn</div>
                </div>
                <div class="lines">
                    <div class="line-item" :style="'--rotate:' + (item * 10) + 'deg'" v-for="item in 36"></div>
                </div>
                <div class="lines">
                    <div class="line-item mini-line" :style="'--rotate:' + (item * 2.5) + 'deg'" v-for="item in 144"></div>
                </div>
                <div class="lines center-line">
                    <div class="line-item" :style="'--rotate:' + (item * 22.5) + 'deg'" v-for="item in 16"></div>
                </div>
            </div>
        </div>
        `,
        methods: {
            close: function(){
                this.$el.classList.remove("open");
            },
            open: function(){
                this.$el.classList.add("open");
            }
        }
    });

    Vue.component('convertcoor', {
        template: `
            <div class="modal" @click="watchClickOutsite($event)">
                <div class="modal-body animate" ref="modalbody">
                    <div class="inner-tab">
                        <div class="modal-title">Chuyển đổi tọa độ</div>
                        <div class="checkpolygon">
                            <div class="province-type-box">
                                <div class="item">
                                    <div class="label">Trục tọa độ</div>
                                    <div class="value">
                                        <select v-model="selected.province_id">
                                            <option v-for="item in provinces" :value="item.id">{{ item.name }} ({{ item.base_coordinate }})</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="d-flex mb-1 mt-1">
                                <div class="flex-1">
                                    <b>Tọa độ X</b>
                                </div>
                                <div class="flex-1">
                                    <b>Tọa độ Y</b>
                                </div>
                            </div>
                            <div class="d-flex mb-05" v-for="(item, index) in vpoint">
                                <div class="flex-1 mr-1">
                                    <input type="text" v-model="item.x" class="default-placeholder" placeholder="1199748.84" pattern="[0-9]*" inputmode="decimal">
                                </div>
                                <div class="flex-1 ml-1 mr-1">
                                    <input type="text" v-model="item.y" class="default-placeholder" placeholder="611245.93" pattern="[0-9]*" inputmode="decimal">
                                </div>
                                <div class="rmicon" @click.stop.prevent="removeRow($event,index)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                            </div>
                            <div class="mt-1 mb-1">
                                <span class="text-link mr-1" @click.stop.prevent="openBatchImport($event)">Nhập tọa độ hàng loạt</span>
                                <span class="text-link" v-if="$root.u" @click.stop.prevent="openImagePicker($event)">Quét tọa độ từ ảnh</span>
                                <input type="file" style="display:none;" ref="scan_image" @change="previewImage($event)" />
                            </div>
                            <div class="d-flex mt-1">
                                <button type="button" class="btn btn-primary mr-1 flex-1" @click.stop.prevent="apply($event)">{{ sending ? 'Chờ kiểm tra ...' : 'Kiểm tra' }}</button>
                                <button type="button" class="btn btn-default ml-1 flex-1" @click.stop.prevent="addRow($event)">+ Thêm tọa độ</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                selected: {
                    province_type: 'old',
                    province_id: null,
                    ward_id: null
                },
                provinces: [],
                vpoint: [{x: '',y: ''},{x: '',y: ''},{x: '',y: ''},{x: '',y: ''},{x: '',y: ''}],
                sending: false,
                reading: false,
                callback: null
            }
        },
        methods: {
            openImagePicker: function(e){
                let vm = this;
                vm.$refs.scan_image.click();
            },
            previewImage: async function(e){
                let vm = this;
                var files = e.target.files;
                if(files[0]){
                    vm.$root.$refs.cropper.open({
                        file: files[0],
                        callback: function(res){
                            if(!res.error){
                                if(res.data.length==0){
                                    vm.$root.showMessageBox("Không đọc được dữ liệu trong ảnh, có thể do ảnh chụp không đủ độ sáng hoặc chất lượng kém vui lòng thử lại ảnh khác !.");
                                }else{
                                    vm.$root.showMessageBox("Quét dữ liệu ảnh thành công, vui lòng kiểm tra lại bảng tọa độ có thể sẽ có sai sót nếu hình ảnh chất lượng không được tốt !.");
                                    vm.vpoint = res.data;
                                }
                            }
                            vm.$refs.scan_image.value = null;
                        }
                    });
                }
            },
            openBatchImport: function(e){
                let vm = this;
                vm.$root.$refs.batch_import.open({
                    callback: function(coors){
                        vm.vpoint = coors;
                    }
                })
            },
            apply: function(event){
                let vm = this;
                if(!vm.$root.e && typeof proj4!='undefined'){
                    vm.$root.e = proj4
                }
                
                let points = [];
                for (let index = 0; index < vm.vpoint.length; index++) {
                    const element = vm.vpoint[index];
                    if(element.x && element.y && element.x!='' && element.y!=''){
                        let valuey = element.y.toString();
                        if(valuey.indexOf('.') == -1 && valuey.indexOf(',') == -1){
                            valuey = valuey + '.00';
                        }
                        valuey = valuey.replace(',','.').replace(',','.').replace(',','.').replace(',','.').split('.');
                        element.y = valuey.map((value, index)=>{
                            return index == valuey.length-1 ? '.' + value : value;
                        }).join('');

                        let valuex = element.x.toString();
                        if(valuex.indexOf('.') == -1 && valuex.indexOf(',') == -1){
                            valuex = valuex + '.00';
                        }
                        valuex = valuex.replace(',','.').replace(',','.').replace(',','.').replace(',','.').split('.');
                        element.x = valuex.map((value, index)=>{
                            return index == valuex.length-1 ? '.' + value : value;
                        }).join('');

                        let x = parseFloat(element.x)>parseFloat(element.y) ? parseFloat(element.x) : parseFloat(element.y);
                        let y = parseFloat(element.x)>parseFloat(element.y) ? parseFloat(element.y) : parseFloat(element.x);
                        let key = vm.$root.e(atob(vm.$root.b),atob(vm.$root.a),[y,x]);
                        points.push({
                            lng: parseFloat(key[0]),
                            lat: parseFloat(key[1]),
                            x: x,
                            y: y,
                        });
                    }
                }

                if(points.length > 0){
                    /* Thêm 1 điểm cuối bằng điểm đầu nếu 2 điểm khác nhau */
                    if(points.length >= 3){
                        let lastPoint = points[points.lenght - 1];
                        let firstPoint = points[0];
                        if(JSON.stringify(lastPoint) != JSON.stringify(firstPoint)){
                            points.push(firstPoint);
                        }
                    }

                    if(typeof vm.callback=='function'){
                        let feature = {
                            type: 'Feature',
                            geometry: points.length >= 3 ? {
                                type: "Polygon",
                                coordinates: [points.map((point)=>{
                                    return [point.lng, point.lat];
                                })]
                            } : {
                                type: "Point",
                                coordinates: [points[0].lng, points[0].lat]
                            },
                            properties: {
                                
                            }
                        }

                        vm.callback({
                            feature: feature
                        });
                    }
                    vm.close();
                }else{
                    vm.$root.showMessageBox("Vui lòng nhập đủ dữ liệu để tiếp tục");
                }
            },
            removeRow: function(e,index){
                if(this.vpoint.length>1){
                    this.vpoint.splice(index,1);
                }else{
                    this.$root.showMessageBox("Không thể xóa tiếp nữa !");
                }
            },
            addRow: function(e){
                this.vpoint.push({
                    x: '',
                    y: ''
                });
            },
            open: function(option){
                let vm = this;
                vm.callback = option && typeof option.callback=='function' ? option.callback : null;
                vm.sending = false;
                vm.selected.province_type = 'old';
                vm.loadProvinces().then(()=>{
                    let lastSelected = window.localStorage.getItem("convert_coor_last_selected_province_id");
                    vm.selected.province_id = lastSelected ? lastSelected : 103;
                });
                vm.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.callback = null;
            },
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            parseCoordinateFromStr: function(str) {
                try {
                    // Bỏ dấu ngoặc
                    let cleaned = str.replace(/[()]/g, '').trim();

                    // Tách số
                    let parts = cleaned.split(',').map(s => s.trim());
                    let a, b;
                    if (parts.length === 4) {
                        // Trường hợp có 4 phần → ghép thành 2 số thập phân
                        a = parseFloat(parts[0] + "." + parts[1]);
                        b = parseFloat(parts[2] + "." + parts[3]);
                    } else if (parts.length === 2) {
                        // Trường hợp chuẩn
                        a = parseFloat(parts[0]);
                        b = parseFloat(parts[1]);
                    } else {
                        return null;
                    }

                    // Kiểm tra lat/lng
                    const isLatA = a >= -90 && a <= 90;
                    const isLatB = b >= -90 && b <= 90;

                    if (isLatA && !isLatB) {
                        return { lat: a, lng: b };
                    } else if (!isLatA && isLatB) {
                        return { lat: b, lng: a };
                    } else {
                        return { lat: a, lng: b }; // fallback
                    }
                } catch (error) {
                    return null;
                }
            },
            loadProvinces: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    let parent_provinces = JSON.parse(JSON.stringify(window.provinces));
                    vm.provinces = parent_provinces.reduce((p, item)=>{
                        p = p.concat(item.childs);
                        return p;
                    }, []);
                    resolve();
                });
            }
        },
        computed: {
            province_selected: function(){
                return this.provinces.find(e => e.id == this.selected.province_id);
            }
        },
        watch: {
            'selected.province_id': function(newval){
                let findProvince = this.provinces.find(e => e.id == newval);
                if(findProvince){
                    this.$root.reloadC(findProvince.base_coordinate);
                    window.localStorage.setItem("convert_coor_last_selected_province_id", newval);
                }
            }
        }
    })

    Vue.component('checkparcel', {
        template: `
            <div class="modal" @click="watchClickOutsite($event)">
                <div class="modal-body animate" ref="modalbody">
                    <div class="tab">
                        <div class="item" :class="activeTab == 1 ? 'active' : ''" @click.stop.prevent="activeTab=1">Bảng góc ranh</div>
                        <div class="item" :class="activeTab == 2 ? 'active' : ''" @click.stop.prevent="activeTab=2">Số tờ thửa</div>
                        <div class="item" :class="activeTab == 3 ? 'active' : ''" @click.stop.prevent="activeTab=3">Tọa độ google</div>
                    </div>
                    <div class="inner-tab">
                        <template v-if="activeTab==2">
                            <div class="checkparcel">
                                <div class="province-type-box">
                                    <template v-if="ward && ward.level == 2">
                                        <div class="item mb-1">
                                            <div class="label mb-05">Hệ thống hành chính</div>
                                            <div class="value">
                                                <select v-model="selected.province_type">
                                                    <option v-for="item in province_types" :value="item.id">{{ item.name }}</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="item mb-1" v-if="selected.province_type == 'old'">
                                            <div class="label mb-05">Khu vực cũ</div>
                                            <div class="value">
                                                <select v-model="selected.ward_id">
                                                    <option v-for="item in wards" :value="item.id">{{ item.name }}</option>
                                                </select>
                                            </div>
                                        </div>
                                    </template>
                                    <div class="item mb-1">
                                        <div class="label mb-05">Số tờ</div>
                                        <div class="value">
                                            <input type="text" v-model="numPage" class="default-placeholder input-sm" placeholder="Nhập số tờ" pattern="[0-9]*" inputmode="decimal">
                                        </div>
                                    </div>
                                    <div class="item mb-1">
                                        <div class="label mb-05">Số thửa</div>
                                        <div class="value">
                                            <input type="text" v-model="numParcel" class="default-placeholder input-sm" placeholder="Nhập số thửa" pattern="[0-9]*" inputmode="decimal">
                                        </div>
                                    </div>
                                </div>
                                <div class="d-flex">
                                    <button type="button" class="btn btn-primary mt-2 w-100" @click.stop.prevent="checkPageAndParcel()">{{ sending ? 'Chờ kiểm tra' : 'Kiểm tra' }}</button>
                                </div>
                            </div>
                        </template>
                        <template v-if="activeTab == 1">
                            <div class="checkpolygon">
                                <template v-if="!reading">
                                    <template v-if="ward && ward.level == 2">
                                        <div class="province-type-box">
                                            <div class="item">
                                                <div class="label">Hệ thống hành chính</div>
                                                <div class="value">
                                                    <select v-model="selected.province_type">
                                                        <option v-for="item in province_types" :value="item.id">{{ item.name }}</option>
                                                    </select>
                                                </div>
                                            </div>
                                            
                                            <div class="item" v-if="selected.province_type == 'old'">
                                                <div class="label">Khu vực cũ</div>
                                                <div class="value">
                                                    <select v-model="selected.province_id">
                                                        <option v-for="item in province.childs" :value="item.id">{{ item.name }}</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                    </template>
                                    <div class="mt-1 mb-1">
                                        <label@click.stop.prevent="openImagePicker($event)" class="text-link mr-05">Quét tọa độ từ ảnh</label>, 
                                        <label class="text-link mr-05" @click.stop.prevent="openSavedPoint($event)" v-if="$root.u && $root.setting && $root.u.phone != $root.setting.trial_phone">chọn từ điểm đã lưu</label>,
                                        <label class="text-link mr-05" @click.stop.prevent="openGroupPoint($event)" v-if="$root.u && $root.setting && $root.u.phone != $root.setting.trial_phone && ($root.u.phone == '0794160374' || $root.u.phone == '0901324268')">chọn từ rổ hàng</label>
                                        <span class="break-line">hoặc nhập vào bảng toạ độ bên dưới (tọa độ VN2000)</span>
                                        <input type="file" style="display:none;" ref="book_coordinates_modal" @change="previewImage($event)" />
                                    </div>
                                    <div class="d-flex mb-1 mt-1">
                                        <div class="flex-1">
                                            <b>Tọa độ X</b>
                                        </div>
                                        <div class="flex-1">
                                            <b>Tọa độ Y</b>
                                        </div>
                                    </div>
                                    <div class="d-flex mb-05" v-for="(item, index) in vpoint">
                                        <div class="flex-1 mr-1">
                                            <input type="text" v-model="item.x" class="default-placeholder" placeholder="1199748.84" pattern="[0-9]*" inputmode="decimal">
                                        </div>
                                        <div class="flex-1 ml-1 mr-1">
                                            <input type="text" v-model="item.y" class="default-placeholder" placeholder="611245.93" pattern="[0-9]*" inputmode="decimal">
                                        </div>
                                        <div class="rmicon" @click.stop.prevent="removeRow($event,index)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                                    </div>
                                    <div class="mt-1 mb-1">
                                        <span class="text-link mr-05" @click.stop.prevent="openBatchImport($event)">Nhập tọa độ hàng loạt</span>
                                    </div>
                                    <div class="d-flex mt-1">
                                        <button type="button" class="btn btn-primary mr-1 flex-1" @click.stop.prevent="apply($event)">{{ sending ? 'Chờ kiểm tra ...' : 'Kiểm tra' }}</button>
                                        <button type="button" class="btn btn-default ml-1 flex-1" @click.stop.prevent="addRow($event)">+ Thêm tọa độ</button>
                                    </div>
                                </template>
                                <template v-else>
                                    <div class="d-flex" style="align-items:center;justify-content:center;height:100px;">
                                        <loading_ios></loading_ios>
                                    </div>
                                </template>
                            </div>
                        </template>
                        <template v-if="activeTab == 3">
                            <div class="checkpolygon">
                                <div class="mt-1">
                                    <span class="break-line">Nhập vào tọa độ lng, lat hoặc link chia sẻ vị trí (google map) vào khung bên dưới sau đó nhấn kiểm tra để xem quy hoạch.</span>
                                </div>
                                <div class="d-flex mb-1 mt-1">
                                    <div class="flex-1">
                                        <b>Tọa độ Lat/Lng hoặc link chia sẻ vị trí</b>
                                    </div>
                                </div>
                                <div class="d-flex mb-1">
                                    <div class="flex-1">
                                        <input type="text" v-model="gpoint" class="default-placeholder" placeholder="10.974871, 106.501154 / https://maps.app.goo.gl/...">
                                    </div>
                                </div>
                                <div class="d-flex mt-1">
                                    <button type="button" class="btn btn-primary mr-1" @click.stop.prevent="gapply($event)">
                                        {{ sending ? 'Chờ kiểm tra ...' : 'Kiểm tra' }}
                                    </button>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                province_types: [{id: 'new', name: '2 cấp'}, {id: 'old', name: '3 cấp'}],
                selected: {
                    province_type: 'old',
                    province_id: null,
                    ward_id: null
                },
                province: null,
                ward: null,
                wards: [],
                allowCheckParcel: true,
                activeTab: 1,
                numPage: '',
                numParcel: '',
                gpoint: '',
                vpoint: [{x: '',y: ''},{x: '',y: ''},{x: '',y: ''},{x: '',y: ''},{x: '',y: ''}],
                sending: false,
                reading: false,
                callback: null
            }
        },
        methods: {
            openImagePicker: function(e){
                let vm = this;
                vm.$refs.book_coordinates_modal.click();
            },
            openBatchImport: function(e){
                let vm = this;
                vm.$root.$refs.batch_import.open({
                    callback: function(coors){
                        vm.vpoint = coors;
                    }
                })
            },
            checkPageAndParcel: function(params){
                let vm = this;
                if(vm.sending) return;
                vm.sending = true;
                vm.$root.postData(vm.$root.setting.api_resource.parcel,{
                    type: vm.selected.province_type,
                    ward_id: vm.selected.province_type == 'old' ? vm.selected.ward_id : vm.ward.id,
                    page: typeof params != 'undefined' ? params.page : vm.numPage,
                    parcel: typeof params != 'undefined' ? params.parcel : vm.numParcel
                }).then((res)=>{
                    vm.sending = false;
                    if(!res.error){
                        let properties = {};
                        properties.html = res.data.properties;
                        properties.area = res.data.parcel && res.data.parcel.hasOwnProperty('area') ? res.data.parcel.area : 0;

                        let feature = {
                            type: "Feature",
                            geometry: JSON.parse(res.data.geometry),
                            properties: properties
                        };

                        vm.callback({
                            feature: feature
                        });

                        vm.close();
                    }else{
                        vm.$root.showMessageBox(res.message);
                    }
                }).catch(function(err){
                    vm.sending = false;
                })
            },
            openSavedPoint: function(event){
                let vm = this;
                vm.$el.classList.remove('open');

                vm.$root.$refs.savedlist.open({
                    callback: function(item){
                        if(item){
                            let geometry = vm.$root.getItemGeometry(item);
                            vm.callback({
                                feature: {
                                    type: "Feature",
                                    geometry: geometry
                                },
                                show_saved_feature: true
                            });
                        }
                    }
                });
            },
            loadAllGroups: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    vm.$root.postData(vm.$root.setting.api_resource.group_list_all, {})
                    .then(res => {
                        resolve(res.data);
                    });
                })
            },
            openGroupPoint: function(e){
                let vm = this;
                vm.$el.classList.remove('open');
                vm.loadAllGroups().then((groups)=>{
                    vm.$root.$refs.action_sheet.open({
                        items: groups,
                        title: 'Chọn rổ hàng',
                        callback: function(selected){
                            if(selected){
                                vm.$el.classList.remove('open');
                                vm.$root.$refs.detailgroup.open({
                                    group: selected,
                                    callback: function(item){
                                        let geometry = vm.$root.getItemGeometry(item);
                                        vm.callback({
                                            feature: {
                                                type: "Feature",
                                                geometry: geometry
                                            }
                                        });
                                    }
                                });
                            }
                        }
                    });
                });
            },
            apply: function(event){
                let vm = this;
                if(!vm.$root.e && typeof proj4!='undefined'){
                    vm.$root.e = proj4
                }
                
                let points = [];
                for (let index = 0; index < vm.vpoint.length; index++) {
                    const element = vm.vpoint[index];
                    if(element.x && element.y && element.x!='' && element.y!=''){
                        let valuey = element.y.toString();
                        if(valuey.indexOf('.') == -1 && valuey.indexOf(',') == -1){
                            valuey = valuey + '.00';
                        }
                        valuey = valuey.replace(',','.').replace(',','.').replace(',','.').replace(',','.').split('.');
                        element.y = valuey.map((value, index)=>{
                            return index == valuey.length-1 ? '.' + value : value;
                        }).join('');

                        let valuex = element.x.toString();
                        if(valuex.indexOf('.') == -1 && valuex.indexOf(',') == -1){
                            valuex = valuex + '.00';
                        }
                        valuex = valuex.replace(',','.').replace(',','.').replace(',','.').replace(',','.').split('.');
                        element.x = valuex.map((value, index)=>{
                            return index == valuex.length-1 ? '.' + value : value;
                        }).join('');

                        let x = parseFloat(element.x)>parseFloat(element.y) ? parseFloat(element.x) : parseFloat(element.y);
                        let y = parseFloat(element.x)>parseFloat(element.y) ? parseFloat(element.y) : parseFloat(element.x);
                        let key = vm.$root.e(atob(vm.$root.b),atob(vm.$root.a),[y,x]);
                        points.push({
                            lng: parseFloat(key[0]),
                            lat: parseFloat(key[1]),
                            x: x,
                            y: y,
                        });
                    }
                }

                if(points.length > 0){
                    /* Thêm 1 điểm cuối bằng điểm đầu nếu 2 điểm khác nhau */
                    if(points.length > 3){
                        let lastPoint = points[points.lenght - 1];
                        let firstPoint = points[0];
                        if(JSON.stringify(lastPoint) != JSON.stringify(firstPoint)){
                            points.push(firstPoint);
                        }
                    }

                    if(typeof vm.callback=='function'){
                        let feature = {
                            type: 'Feature',
                            geometry: points.length > 4 ? {
                                type: "Polygon",
                                coordinates: [points.map((point)=>{
                                    return [point.lng, point.lat];
                                })]
                            } : {
                                type: "Point",
                                coordinates: [points[0].lng, points[0].lat]
                            },
                            properties: {
                                page: 0,
                                parcel: 0,
                                new_ward_id: vm.ward.id
                            }
                        }

                        vm.callback({
                            feature: feature
                        });
                    }
                    vm.close();
                }else{
                    vm.$root.showMessageBox("Vui lòng nhập đủ dữ liệu để tiếp tục");
                }
            },
            gapply: function(event){
                let vm = this;
                if(!vm.$root.e && typeof proj4!='undefined'){
                    vm.$root.e = proj4
                }
                
                let points = [];
                vm.sending = true;
                vm.getPointFromInput(vm.gpoint).then((point)=>{
                    if(point){
                        vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                            lng: point.lng,
                            lat: point.lat
                        }).then((res)=>{
                            vm.sending = false;
                            if(!res.error && res.data){
                                if(typeof vm.callback == 'function'){
                                    let feature = {
                                        type: 'Feature',
                                        geometry: {
                                            type: "Point",
                                            coordinates: [point.lng, point.lat]
                                        },
                                        properties: {
                                            page: 0,
                                            parcel: 0,
                                            new_ward_id: vm.ward.id,
                                            html: res.data.html
                                        }
                                    }

                                    vm.callback({
                                        feature: feature
                                    });
                                }
                                vm.close();
                            }
                        })
                    }else{
                        vm.sending = false;
                        vm.$root.showMessageBox("Vui lòng nhập đủ dữ liệu để tiếp tục");
                    }
                });
            },
            getPointFromInput: function(str){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    if(str.indexOf('https://') > -1){
                        vm.$root.postData(vm.$root.setting.api_resource.url_to_point, {
                            url: str
                        }).then((res)=>{
                            if(!res.error && res.data){
                                resolve(res.data);
                            }else{
                                if(res.message){
                                    vm.$root.showMessageBox(res.message);
                                }
                            }
                        })
                    }else{
                        resolve(vm.parseCoordinateFromStr(str));
                    }
                })
            },
            parseCoordinateFromStr: function(str) {
                try {
                    // Bỏ dấu ngoặc
                    let cleaned = str.replace(/[()]/g, '').trim();

                    // Tách số
                    let parts = cleaned.split(',').map(s => s.trim());
                    let a, b;
                    if (parts.length === 4) {
                        // Trường hợp có 4 phần → ghép thành 2 số thập phân
                        a = parseFloat(parts[0] + "." + parts[1]);
                        b = parseFloat(parts[2] + "." + parts[3]);
                    } else if (parts.length === 2) {
                        // Trường hợp chuẩn
                        a = parseFloat(parts[0]);
                        b = parseFloat(parts[1]);
                    } else {
                        return null;
                    }

                    // Kiểm tra lat/lng
                    const isLatA = a >= -90 && a <= 90;
                    const isLatB = b >= -90 && b <= 90;

                    if (isLatA && !isLatB) {
                        return { lat: a, lng: b };
                    } else if (!isLatA && isLatB) {
                        return { lat: b, lng: a };
                    } else {
                        return { lat: a, lng: b }; // fallback
                    }
                } catch (error) {
                    return null;
                }
            },
            removeRow: function(e,index){
                if(this.vpoint.length>1){
                    this.vpoint.splice(index,1);
                }else{
                    this.$root.showMessageBox("Không thể xóa tiếp nữa !");
                }
            },
            addRow: function(e){
                this.vpoint.push({
                    x: '',
                    y: ''
                });
            },
            previewImage: async function(e){
                let vm = this;
                var files = e.target.files;
                if(files[0]){
                    vm.$root.$refs.cropper.open({
                        file: files[0],
                        callback: function(res){
                            if(!res.error){
                                if(res.data.length==0){
                                    vm.$root.showMessageBox("Không đọc được dữ liệu trong ảnh, có thể do ảnh chụp không đủ độ sáng hoặc chất lượng kém vui lòng thử lại ảnh khác !.");
                                }else{
                                    vm.$root.showMessageBox("Quét dữ liệu ảnh thành công, vui lòng kiểm tra lại bảng tọa độ có thể sẽ có sai sót nếu hình ảnh chất lượng không được tốt !.");
                                    vm.vpoint = res.data;
                                }
                            }
                            vm.$refs.book_coordinates_modal.value = null;
                        }
                    });
                }
            },
            open: function(option){
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.ward = option && typeof option.ward!='undefined' ? option.ward : null;
                this.province = option && typeof option.province!='undefined' ? option.province : null;
                this.allowCheckParcel  = option && typeof option.allowCheckParcel!='undefined' ? option.allowCheckParcel : false;
                this.wards = [];
                this.sending = false;
                if(this.ward.level == 2){
                    this.loadWardsGroup();
                    this.setDefaultProvince();
                }else{
                    this.selected.ward_id = this.ward.id;
                    this.selected.province_type = 'old';
                    this.selected.province_id = this.province.id;
                    this.loadWards();
                    
                    this.$root.reloadC(this.province.base_coordinate);
                }
                this.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.callback = null;
            },
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            parseCoordinateFromStr: function(str) {
                try {
                    // Bỏ dấu ngoặc
                    let cleaned = str.replace(/[()]/g, '').trim();

                    // Tách số
                    let parts = cleaned.split(',').map(s => s.trim());
                    let a, b;
                    if (parts.length === 4) {
                        // Trường hợp có 4 phần → ghép thành 2 số thập phân
                        a = parseFloat(parts[0] + "." + parts[1]);
                        b = parseFloat(parts[2] + "." + parts[3]);
                    } else if (parts.length === 2) {
                        // Trường hợp chuẩn
                        a = parseFloat(parts[0]);
                        b = parseFloat(parts[1]);
                    } else {
                        return null;
                    }

                    // Kiểm tra lat/lng
                    const isLatA = a >= -90 && a <= 90;
                    const isLatB = b >= -90 && b <= 90;

                    if (isLatA && !isLatB) {
                        return { lat: a, lng: b };
                    } else if (!isLatA && isLatB) {
                        return { lat: b, lng: a };
                    } else {
                        return { lat: a, lng: b }; // fallback
                    }
                } catch (error) {
                    return null;
                }
            },
            loadWards: function(){
                let vm = this;
                if(vm.wards.length == 0){
                    vm.$root.postData(vm.$root.setting.api_resource.child_level3,{
                        parent_id: vm.ward.district_id
                    }).then((res)=>{
                        if(res.data){
                            vm.wards = res.data.map((e)=>{
                                e.ward_id = e.id;
                                return e;
                            });
                        }
                    });
                }
            },
            loadWardsGroup: function(){
                let vm = this;
                if(vm.wards.length == 0){
                    vm.$root.postData(vm.$root.setting.api_resource.group_wards,{
                        ward_id: vm.ward.id
                    }).then((res)=>{
                        if(res.data){
                            vm.wards = res.data;
                            vm.selected.ward_id = res.data[0].id;
                        }
                    });
                }
            },
            setDefaultProvince: function(){
                let findMain = this.province ? this.province.childs.find(e => e.is_main) : null;
                if(findMain){
                    this.selected.province_id = findMain.id;
                    this.$root.reloadC(findMain.base_coordinate);
                }
            }
        },
        computed: {
            province_type: function(){
                return this.province_types.find(e => e.id == this.selected.province_type);
            },
            province_selected: function(){
                if(this.selected.province_type == 'new'){
                    return this.province ? this.province.childs.find(e => e.id == this.selected.province_id) : null;
                }else{
                    let parent_provinces = JSON.parse(JSON.stringify(this.$root.provinces));
                    let provinces = parent_provinces.reduce((p, item)=>{
                        p = p.concat(item.childs);
                        return p;
                    }, []);
                    return provinces.find(e => e.id == this.selected.province_id);
                }
            },
            ward_selected: function(){
                return this.wards ? this.wards.find(e => e.id == this.selected.ward_id) : null;
            }
        },
        watch: {
            'selected.province_id': function(newval){
                var findProvince = null;
                if(this.selected.province_type == 'new'){
                    findProvince = this.province.childs.find(e => e.id == newval);
                }else{
                    let parent_provinces = JSON.parse(JSON.stringify(this.$root.cities));
                    let provinces = parent_provinces.reduce((p, item)=>{
                        p = p.concat(item.childs);
                        return p;
                    }, []);
                    findProvince = provinces.find(e => e.id == newval);
                }

                if(findProvince){
                    this.$root.reloadC(findProvince.base_coordinate);
                }
            }
        }
    });

    Vue.component('cropper', {
        template: `
            <div class="cropper-box">
                <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="modal-title">Quét bảng góc ranh</div>
                <div class="img-cropper" v-show="!sending">
                    <div>
                        <img ref="image" src="">
                    </div>
                </div>
                <div class="img-cropper" v-if="sending">
                    <div>
                        <div>
                            <loading_ios class="gray"></loading_ios>
                        </div>
                        <div style="color:#ccc;">Đang xử lý ảnh...</div>
                    </div>
                </div>
                <div class="btn-block" v-if="!sending">
                    <button class="btn-primary mr-1" @click.stop.prevent="apply()">Xác nhận</button>
                    <button class="btn-default mr-1" @click.stop.prevent="cancel()">Hủy thao tác</button>
                </div>
            </div>
        `,
        data: function(){
            return {
                src: null,
                cropper: null,
                sending: false,
                cancel_state: false,
                callback: null,
                origin_file: null
            }
        },
        methods:{
            apply: function(){
                let vm = this;
                let canvas = vm.cropper.getCroppedCanvas();
                if(canvas){
                    canvas.toBlob((blob)=>{
                        vm.sending = true;
                        vm.$root.postFileData(vm.$root.setting.api_resource.ocr, {
                            file: blob
                        }).then((res)=>{
                            if(typeof vm.callback == 'function'){
                                if(!vm.cancel_state){
                                    vm.callback(res);
                                }
                            }

                            vm.close();
                        });
                    })
                }
            },
            readImageAsync: function(file) {
                return new Promise((resolve, reject) => {
                    var reader = new FileReader();
                    reader.onload = function(event) {
                        var data = event.target.result;
                        resolve(data);
                    };
                    
                    reader.readAsDataURL(file);
                });
            },
            open: function(option){
                let vm = this;
                vm.cancel_state = false;
                vm.callback = option && typeof option.callback=='function' ? option.callback : null;
                vm.origin_file = option.file;
                vm.$el.classList.add('open');
                vm.readImageAsync(option.file).then((result)=>{
                    vm.$refs.image.src = result;
                    setTimeout(()=>{
                        if(vm.cropper){
                            vm.cropper.destroy();
                            vm.cropper = null;
                        }

                        vm.cropper = new Cropper(vm.$refs.image, {
                            viewMode: 1,
                            dragMode: 'move',
                            aspectRatio: 6 / 8,
                            autoCropArea: option.file.size < 512000 ? 1 : 0.7,
                            restore: false,
                            guides: false,
                            center: false,
                            highlight: false,
                            cropBoxMovable: false,
                            cropBoxResizable: option.file.size < 512000 ? false : true,
                            zoomable: true,
                            toggleDragModeOnDblclick: false,
                        });
                    }, 50)
                });
            },
            cancel: function(){
                this.cancel_state = true;
                this.sending = false;
                this.$el.classList.remove('open');
            },
            close: function() {
                this.sending = false;
                this.cancel_state = true;
                this.$el.classList.remove('open');
            }
        }
    });

    Vue.component('batch_import', {
        template: `
            <div class="modal" @click="watchClickOutsite($event)">
                <div class="modal-body animate" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Nhập tọa độ hàng loạt</div>
                    <div class="mb-1">Bạn có thể dán toàn bộ tọa độ vào khung bên dưới đây sao cho mỗi dòng là 1 cặp tọa độ ví dụ : 1199748.84, 611245.93</div>
                    <div class="d-flex pb-1">
                        <div class="flex-1">
                            <textarea v-model="text" style="height: 200px;"></textarea>
                        </div>
                    </div>
                    <div class="login">
                        <div class="d-flex mt-1">
                            <button class="btn btn-primary mr-1" style="flex:1;" @click.stop.prevent="apply($event)">Xác nhận</button>
                            <button class="btn btn-default" style="flex:1;" @click.stop.prevent="clear($event)">Xóa làm lại</button>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                text: '',
                callback: null
            }
        },
        methods: {
            clear: function(e){
                this.text = '';
            },
            apply: function(e){
                const regex = /(\d{2}(.|,)?\d{4,5}(.|,)\d{1,4})/g;

                let arr = [];
                let textList = this.text.split('\n');
                for (let index = 0; index < textList.length; index++) {
                    const text = textList[index];
                    console.log(text);
                    const matches = text.match(regex);
                    if(matches && matches.length == 2){
                        arr.push({
                            x: matches[0],
                            y: matches[1]
                        });
                    }
                }

                if(arr.length > 0){
                    this.close();
                    this.callback(arr);
                }else{
                    this.$root.showMessageBox("Không thể lấy được dữ liệu tọa độ từ dữ liệu bạn đã nhập vui lòng kiểm tra lại dữ liệu sau đó thử lại");
                }
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            },
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
        }
    });

    Vue.component('savedlist', {
        template: `
        <div class="modal modal-center">
            <div class="modal-body animate" ref="modalbody">
                <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="modal-title">Điểm đã lưu</div>
                <div class="savedlist">
                    <div class="quick-search">
                        <div class="icon"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="search" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="svg-inline--fa fa-search fa-w-16 fa-3x"><path fill="currentColor" d="M508.5 481.6l-129-129c-2.3-2.3-5.3-3.5-8.5-3.5h-10.3C395 312 416 262.5 416 208 416 93.1 322.9 0 208 0S0 93.1 0 208s93.1 208 208 208c54.5 0 104-21 141.1-55.2V371c0 3.2 1.3 6.2 3.5 8.5l129 129c4.7 4.7 12.3 4.7 17 0l9.9-9.9c4.7-4.7 4.7-12.3 0-17zM208 384c-97.3 0-176-78.7-176-176S110.7 32 208 32s176 78.7 176 176-78.7 176-176 176z"></path></svg></div>
                        <input type="text" autocomplete="off" v-model="keyword" autofill="off" placeholder="Tìm từ khóa" />
                    </div>
                    <div class="items">
                        <template v-if="data.length > 0">
                            <template v-for="(item, index) in data">
                                <div class="item has-action" @click.stop.prevent="showOption($event, item)">
                                    <div class="name">{{ item.name }}</div>
                                    <div class="note" v-if="item.note != ''">{{ item.note }}</div>
                                    <div class="remain">Ngày lưu: {{ item.created_at | full-time }}</div>
                                </div>
                            </template>
                            <div class="d-flex btn btn-default" v-if="!loading && has_more_data" @click.stop.prevent="loadMore($event)">Tải thêm dữ liệu</div>
                        </template>
                        <template v-if="data.length == 0 && !loading">
                            <div class="pt-1 pb-1 mt-1 mb-1" style="text-align:center;">{{ keyword != '' ? 'Không tìm thấy kết quả phù hợp' : 'Không tìm thấy danh sách điểm đã lưu' }}</div>
                        </template>

                        <template v-if="loading">
                            <loading_ios></loading_ios>
                        </template>
                    </div>
                </div>
            </div>
        </div>
        `,
        filters: {
            'full-time': function(timestamp){
                timestamp = Number(timestamp);
                // Nếu timestamp là giây, chuyển sang milliseconds
                if (timestamp.toString().length === 10) {
                    timestamp *= 1000;
                }

                const date = new Date(timestamp);

                const dd = String(date.getDate()).padStart(2, '0');
                const mm = String(date.getMonth() + 1).padStart(2, '0'); // Tháng bắt đầu từ 0
                const yyyy = date.getFullYear();

                const hh = String(date.getHours()).padStart(2, '0');
                const ii = String(date.getMinutes()).padStart(2, '0');

                return `${dd}/${mm}/${yyyy} ${hh}:${ii}`;
            }
        },
        data: function(){
            return {
                loading: false,
                data: [],
                page: 0,
                keyword: '',
                timeout: null,
                has_more_data: true,
                callback: null
            }
        },
        methods: {
            loadMore: function(){
                if(this.has_more_data){
                    this.page = this.page + 1;
                }
            },
            showOption: function(event, item){
                let vm = this;
                if(typeof vm.callback == 'function'){
                    vm.callback(item);
                    vm.close();
                    return;
                }
                
                let selectitems = [
                    {
                        name: 'Xem bản đồ quy hoạch',
                        id: 'plan'
                    },
                    {
                        name: 'Thêm vào rổ hàng mới',
                        id: 'addtonewgroup'
                    },
                    {
                        name: 'Thêm vào rổ hàng đã có',
                        id: 'addtogroup'
                    },
                    {
                        name: 'Chia sẻ cho tài khoản khác',
                        id: 'share'
                    },
                    {
                        name: 'Xem bảng tọa độ ranh',
                        id: 'viewcooordinate'
                    },
                    {
                        name: 'Chỉnh sửa thông tin',
                        id: 'changename'
                    },
                    {
                        name: 'Xóa điểm',
                        id: 'remove'
                    },
                ];

                vm.$root.$refs.action_sheet.open({
                    items: selectitems,
                    title: 'Chọn thao tác sử dụng',
                    callback: function(e){
                        if(e){
                            switch (e.id) {
                                case 'plan':
                                    vm.viewPlanMap(item);
                                    break;
                                case 'viewcooordinate':
                                    vm.viewCoordinate(item);
                                    break;
                                case 'changename':
                                    vm.editPoint(item);
                                    break;
                                case 'remove':
                                    vm.removePoint(item);
                                    break;
                                case 'share':
                                    vm.shareAccount(item);
                                    break;
                                case 'addtonewgroup':
                                    vm.addToNewGroup(item);
                                    break;
                                case 'addtogroup':
                                    vm.addToGroup(item);
                                    break;
                                default:
                                    break;
                            }
                        }
                    }
                });
            },
            addToNewGroup: function(item){
                let vm = this;
                vm.$root.$refs.addgroup.open({
                    title: 'Tạo mới rổ hàng',
                    callback: function(id){
                        if(id){
                            let newitem = JSON.parse(JSON.stringify(item));
                            newitem.name = encodeURIComponent(newitem.name);
                            newitem.note = encodeURIComponent(newitem.note);
                            newitem.geometry = vm.$root.getItemGeometry(newitem);
                            vm.$root.postData(vm.$root.setting.api_resource.add_to_group, {
                                group_id: id,
                                item: newitem
                            })
                            .then(res => {
                                vm.$root.showMessageBox(res.message);
                            });
                        }
                    }
                })
            },
            addToGroup: function(item){
                let vm = this;
                vm.loadAllGroups().then((result)=>{
                    vm.$root.$refs.action_sheet.open({
                        items: result,
                        title: 'Chọn rổ hàng',
                        callback: function(e){
                            if(e){
                                let newitem = JSON.parse(JSON.stringify(item));
                                newitem.name = encodeURIComponent(newitem.name);
                                newitem.note = encodeURIComponent(newitem.note);
                                newitem.geometry = vm.$root.getItemGeometry(newitem);
                                
                                vm.$root.postData(vm.$root.setting.api_resource.add_to_group, {
                                    group_id: e.id,
                                    item: newitem
                                })
                                .then(res => {
                                    vm.$root.showMessageBox(res.message);
                                });
                            }
                        }
                    });
                })
            },
            loadAllGroups: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    vm.$root.postData(vm.$root.setting.api_resource.group_list_all, {})
                    .then(res => {
                        resolve(res.data);
                    });
                })
            },
            shareAccount: function(item){
                let vm = this;
                vm.$root.$refs.shareaccount.open({
                    callback: function(phone){
                        vm.$root.postData(vm.$root.setting.api_resource.share_point, {
                            phone: phone,
                            geometry: vm.$root.getItemGeometry(item)
                        }).then(res => {
                            vm.$root.showMessageBox(res.message);
                        });
                    }
                });
            },
            editPoint: function(item){
                let vm = this;
                vm.$root.$refs.updatepoint.open({
                    form: {
                        id: item.id,
                        name: item.name,
                        note: item.note
                    },
                    callback: function(newform){
                        vm.$el.classList.add('open');
                        if(newform){
                            let index = vm.data.findIndex((el)=>{
                                return el.id == item.id
                            });

                            vm.data[index].name = newform.name;
                            vm.data[index].note = newform.note;
                        }
                    }
                });
            },
            viewCoordinate: function(item){
                let vm = this;
                let geometry = vm.$root.getItemGeometry(item);

                if(geometry){
                    let centerPoint = vm.$root.getCenterGeometry(geometry);
                    vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                        lng: centerPoint.lng,
                        lat: centerPoint.lat
                    }).then((res)=>{
                        if(!res.error && res.data && res.data.province){
                            let provinces = JSON.parse(JSON.stringify(window.provinces));
                            let province = provinces.find(e => e.id == res.data.province.id);
                            if(province){
                                let mainProvince = province.childs.find(item => item.is_main);
                                if(mainProvince){
                                    vm.$root.reloadC(mainProvince.base_coordinate);
                                    let points = vm.$root.getGeometryCoordinates(geometry);
                                    points = points.map((point)=>{
                                        let lng = point[0];
                                        let lat = point[1];

                                        let vn2000Point = vm.$root.e(atob(vm.$root.b),atob(vm.$root.a)).inverse([lng, lat]);
                                        return {
                                            lng: Number(lng.toFixed(10)),
                                            lat: Number(lat.toFixed(10)),
                                            x: Number(vn2000Point[0].toFixed(3)),
                                            y: Number(vn2000Point[1].toFixed(3))
                                        };
                                    });

                                    vm.$root.$refs.coordinatetable.open({
                                        points: points,
                                        base_coordinate: mainProvince.base_coordinate
                                    });
                                }
                            }
                        }
                    });
                }
            },
            removePoint: function(item){
                let vm = this;
                vm.$root.showConfirmBox({
                    message: 'Bạn chắc chắn muốn xóa điểm đã lưu này ?',
                    callback: function(confirm){
                        if(confirm){
                            vm.loading = true;
                            vm.$root.postData(vm.$root.setting.api_resource.remove_saved_point, {
                                id: item.id
                            })
                            .then(res => {
                                vm.$el.classList.add('open');
                                vm.$root.showMessageBox(res.message);
                                vm.reloadResource();
                            });
                        }else{
                            vm.$el.classList.add('open');
                        }
                    }
                })
            },
            reloadResource: function(){
                this.data = [];
                if(this.page == 0){
                    this.loadResource();    
                }else{
                    this.page = 0;    
                }
            },
            viewPlanMap: function(item){
                let vm = this;
                vm.close();
                let geometry = vm.$root.getItemGeometry(item);

                if(geometry){
                    let centerPoint = vm.$root.getCenterGeometry(geometry);
                    vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                        lng: centerPoint.lng,
                        lat: centerPoint.lat
                    }).then((res)=>{
                        if(!res.error && res.data && res.data.province){
                            let provinces = JSON.parse(JSON.stringify(window.provinces));
                            let province = provinces.find(e => e.id == res.data.province.id);
                            if(province){
                                vm.$root.$refs['app-map'].setMap({
                                    ward: res.data.ward,
                                    province: province,
                                    feature: {
                                        type: 'Feature',
                                        geometry: geometry
                                    }
                                });
                            }
                        }else{
                            vm.$root.showMessageBox('Không thể xác định vị trí dựa theo tọa độ của điểm này');
                        }
                    })
                }
            },
            loadResource: function(){
                let vm = this;
                vm.loading = true;
                vm.$root.postData(vm.$root.setting.api_resource.saved_list, {
                    keyword: encodeURIComponent(vm.keyword),
                    page: vm.page
                })
                .then(res => {
                    vm.loading = false;
                    res.data.forEach((item)=>{
                        vm.data.push(item);
                    });

                    vm.has_more_data = res.has_more;
                });
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.$el.classList.add('open');
                this.data = [];

                if(this.page != 0){
                    this.page = 0;
                }else if(this.keyword != ''){
                    this.keyword = '';
                }else{
                    this.loadResource();
                }
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        watch: {
            page: function(){
                this.loading = true;
                clearTimeout(this.timeout);
                this.timeout = setTimeout(()=>{
                    this.loadResource();
                }, 400)
            },
            keyword: function(){
                this.loading = true;
                this.page = 0;
                this.has_more_data = true;
                this.data = [];
                clearTimeout(this.timeout);
                this.timeout = setTimeout(()=>{
                    this.loadResource();
                }, 500)
            }
        }
    });

    Vue.component('updatepoint', {
        template: `
            <div class="modal modal-center" @click="watchClickOutsite($event)">
                <div class="modal-body animate" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Cập nhật điểm</div>
                    <div class="login">
                        <div class="d-flex">
                            <div class="flex-1">
                                <label class="sub-title">Tên điểm</label>
                                <input type="text" v-model="form.name" />
                            </div>
                        </div>
                        <div class="d-flex mt-1">
                            <div class="flex-1">
                                <label class="sub-title">Ghi chú điểm</label>
                                <textarea v-model="form.note"></textarea>
                            </div>
                        </div>
                        <div class="d-flex mt-1">
                            <button class="btn-sm btn-primary mr-1" @click.stop.prevent="update($event)">{{ sending ? 'Đang lưu...' : 'Cập nhật' }}</button>
                            <button class="btn-sm btn-default mr-1" @click.stop.prevent="cancel($event)">Hủy thao tác</button>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                form: {
                    id: '',
                    name: '',
                    note: ''
                },
                callback: null,
                sending: false
            }
        },
        methods: {
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            update: function(){
                let vm = this;
                vm.sending = true;
                let form = JSON.parse(JSON.stringify(vm.form));
                form.name = encodeURIComponent(form.name);
                form.note = encodeURIComponent(form.note);
                vm.$root.postData(vm.$root.setting.api_resource.update_point, form).then(res => {
                    vm.sending = false;
                    if(!res.error){
                        vm.$root.showMessageBox(res.message);
                        if(typeof vm.callback == 'function'){
                            vm.callback(JSON.parse(JSON.stringify(vm.form)));
                        }
                    }
                    vm.close();
                });
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.form = option && typeof option.form != 'undefined' ? option.form : {
                    id: '',
                    name: '',
                    note: ''
                };
                this.$el.classList.add('open');
            },
            cancel: function(){
                if(typeof this.callback == 'function'){
                    this.callback(false);
                }
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        }
    });

    Vue.component('shareaccount', {
        template: `
            <div class="modal modal-center" @click="watchClickOutsite($event)">
                <div class="modal-body animate" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Chia sẻ điểm</div>
                    <div class="sharecode">
                        <div class="mb-1">Nhập số điện thoại của tài khoản bạn muốn chia sẻ điểm này vào khung dưới đây</div>
                        <div class="otpform">
                            <input type="text" ref="phone" v-model="phone" inputmode="decimal" />
                        </div>
                        <div class="d-flex mt-1">
                            <button class="btn btn-primary mt-1 flex-1" :disabled="sending" @click.stop.prevent="apply($event)">Xác nhận</button>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                item: null,
                phone: '',
                sending: false,
                callback: null
            }
        },
        methods: {
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            apply: function(e){
                let vm = this;
                if(vm.phone.length < 9){
                    vm.$root.showMessageBox('Vui lòng nhập đủ số điện thoại');
                    return;
                }

                vm.callback(vm.phone);
                vm.close();
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.phone = '';
                this.callback = typeof option.callback == 'function' ? option.callback : null;
                this.$el.classList.add('open');
                setTimeout(()=>{
                    this.$refs.phone.focus();
                }, 500)
            },
            close: function(e) {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        watch: {
            
        }
    });

    Vue.component('grouplist', {
        template: `
        <div class="modal modal-center">
            <div class="modal-body animate" ref="modalbody">
                <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="modal-title">Rổ hàng</div>
                <div class="grouplist">
                    <div class="quick-search">
                        <div class="icon"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="search" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="svg-inline--fa fa-search fa-w-16 fa-3x"><path fill="currentColor" d="M508.5 481.6l-129-129c-2.3-2.3-5.3-3.5-8.5-3.5h-10.3C395 312 416 262.5 416 208 416 93.1 322.9 0 208 0S0 93.1 0 208s93.1 208 208 208c54.5 0 104-21 141.1-55.2V371c0 3.2 1.3 6.2 3.5 8.5l129 129c4.7 4.7 12.3 4.7 17 0l9.9-9.9c4.7-4.7 4.7-12.3 0-17zM208 384c-97.3 0-176-78.7-176-176S110.7 32 208 32s176 78.7 176 176-78.7 176-176 176z"></path></svg></div>
                        <input type="text" autocomplete="off" v-model="keyword" autofill="off" placeholder="Tìm từ khóa" />
                        <button class="btn btn-primary ml-1" @click.stop.prevent="addNewGroup($event)">+ Tạo mới</button>
                    </div>
                    <div class="items">
                        <template v-if="data.length > 0">
                            <template v-for="(item, index) in data">
                                <div class="item has-action" @click.stop.prevent="showOption($event, item)">
                                    <div class="name">{{ item.name }}</div>
                                    <div class="is-shared" v-if="item.isShared">Được chia sẻ</div>
                                    <div class="properties">
                                        <div class="records">Số hàng: {{ item.total }}</div>
                                        <div class="persons">Thành viên: {{ item.viewer }}</div>
                                        <div class="remain">Ngày tạo: {{ item.created_at | full-time }}</div>
                                    </div>
                                </div>
                            </template>
                            <div class="d-flex btn btn-default" v-if="!loading && has_more_data" @click.stop.prevent="loadMore($event)">Tải thêm dữ liệu</div>
                        </template>
                        <template v-if="data.length == 0 && !loading">
                            <div class="pt-1 pb-1 mt-1 mb-1" style="text-align:center;">{{ keyword != '' ? 'Không tìm thấy kết quả phù hợp' : 'Không tìm thấy danh sách điểm đã lưu' }}</div>
                        </template>

                        <template v-if="loading">
                            <loading_ios></loading_ios>
                        </template>
                    </div>
                </div>
            </div>
        </div>
        `,
        data: function(){
            return {
                loading: false,
                data: [],
                page: 0,
                keyword: '',
                timeout: null,
                has_more_data: true,
                callback: null
            }
        },
        filters: {
            'full-time': function(timestamp){
                timestamp = Number(timestamp);
                // Nếu timestamp là giây, chuyển sang milliseconds
                if (timestamp.toString().length === 10) {
                    timestamp *= 1000;
                }

                const date = new Date(timestamp);

                const dd = String(date.getDate()).padStart(2, '0');
                const mm = String(date.getMonth() + 1).padStart(2, '0'); // Tháng bắt đầu từ 0
                const yyyy = date.getFullYear();

                const hh = String(date.getHours()).padStart(2, '0');
                const ii = String(date.getMinutes()).padStart(2, '0');

                return `${dd}/${mm}/${yyyy} ${hh}:${ii}`;
            }
        },
        methods: {
            reloadList: function(){
                this.data = [];
                if(this.page == 0 && this.keyword == ''){
                    this.loadResource();
                }else{
                    this.page = 0;
                    this.keyword = '';
                }
            },
            loadMore: function(){
                if(this.has_more_data){
                    this.page = this.page + 1;
                }
            },
            addNewGroup: function(e){
                let vm = this;
                vm.$root.$refs.addgroup.open({
                    title: 'Tạo mới rổ hàng',
                    callback: function(){
                        vm.reloadList();
                    }
                });
            },
            showOption: function(event, item){
                let vm = this;

                let selectitems = [
                    {
                        name: 'Xem chi tiết rổ hàng',
                        id: 'detail'
                    },
                    {
                        name: 'Danh sách thành viên',
                        id: 'permission'
                    },
                    {
                        name: 'Đổi tên rổ hàng',
                        id: 'changename'
                    }
                ];

                if(item.isShared){
                    if(!item.hasEditPermission){
                        selectitems = [
                            {
                                name: 'Xem chi tiết rổ hàng',
                                id: 'detail'
                            },
                            {
                                name: 'Thoát khỏi rổ hàng',
                                id: 'outgroup'
                            }
                        ];
                    }else{
                        selectitems.push({
                            name: 'Thoát khỏi rổ hàng',
                            id: 'outgroup'
                        });
                    }
                }else{
                    selectitems.push({
                        name: 'Xóa rổ hàng',
                        id: 'remove'
                    });
                }

                vm.$root.$refs.action_sheet.open({
                    items: selectitems,
                    title: 'Chọn thao tác sử dụng',
                    callback: function(e){
                        if(e){
                            switch (e.id) {
                                case 'permission':
                                    vm.openPermissionList(item);
                                    break;
                                case 'changename':
                                    vm.openEditGroup(item);
                                    break;
                                case 'remove':
                                    vm.removeItem(item);
                                    break;
                                case 'detail':
                                    vm.detailGroup(item);
                                    break;
                                case 'outgroup':
                                    vm.outGroup(item);
                                    break;
                                default:
                                    break;
                            }
                        }
                    }
                });
            },
            outGroup: function(item){
                let vm = this;
                vm.$root.showConfirmBox({
                    message: 'Bạn chắc chắn muốn thoát khỏi rổ hàng này ?',
                    callback: function(confirm){
                        if(confirm){
                            vm.loading = true;
                            vm.$root.postData(vm.$root.setting.api_resource.v1_out_group, {
                                group_id: item.id
                            })
                            .then(res => {
                                vm.$root.showMessageBox(res.message);
                                vm.reloadList();
                            });
                        }else{
                            vm.$el.classList.add('open');
                        }
                    }
                })
            },
            detailGroup: function(item){
                let vm = this;
                vm.$root.$refs.detailgroup.open({
                    group: item
                });
            },
            openEditGroup: function(item){
                let vm = this;
                vm.$root.$refs.addgroup.open({
                    title: 'Đổi tên rổ hàng',
                    form: {
                        name: item.name,
                        id: item.id
                    },
                    callback: function(id, form, message){
                        let findIndex = vm.data.findIndex(e => e.id == id);
                        if(findIndex > -1){
                            vm.data[findIndex].name = form.name;
                            vm.$root.showMessageBox(message);
                        }
                    }
                });
            },
            openPermissionList: function(item){
                let vm = this;
                vm.$root.$refs.permissionlist.open({
                    group: item,
                    callback: function(person){
                        let findIndex = vm.data.findIndex(e => e.id == item.id);
                        if(findIndex > -1){
                            vm.data[findIndex].viewer = person;
                        }
                    }
                });
            },
            removeItem: function(item){
                let vm = this;
                vm.$root.showConfirmBox({
                    message: 'Bạn chắc chắn muốn xóa rổ hàng này ?',
                    callback: function(confirm){
                        if(confirm){
                            vm.loading = true;
                            vm.$root.postData(vm.$root.setting.api_resource.remove_group, {
                                id: item.id
                            })
                            .then(res => {
                                vm.$root.showMessageBox(res.message);
                                vm.reloadList();
                            });
                        }else{
                            vm.$el.classList.add('open');
                        }
                    }
                })
            },
            loadResource: function(){
                let vm = this;
                vm.loading = true;
                vm.$root.postData(vm.$root.setting.api_resource.group_list, {
                    page: vm.page,
                    keyword: encodeURIComponent(vm.keyword)
                })
                .then(res => {
                    vm.loading = false;

                    res.data.map((item)=>{
                        let findTotal = res.group_total.find((e)=>{
                            return e.group_id == item.id;
                        });
                        item.total = findTotal ? parseInt(findTotal.total) : 0;

                        let findViewer = res.group_viewer.find((e)=>{
                            return e.group_id == item.id;
                        });
                        item.viewer = findViewer ? parseInt(findViewer.total) : 0;
                        item.isShared = res.share_ids.indexOf(parseInt(item.id)) > -1 ? true : false;
                        item.hasEditPermission = res.edit_permission_ids.indexOf(parseInt(item.id)) > -1 ? true : false;
                        vm.data.push(item);
                    });

                    vm.has_more_data = res.has_more;
                });
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.$el.classList.add('open');
                this.data = [];

                if(this.page != 0){
                    this.page = 0;
                }else if(this.keyword != ''){
                    this.keyword = '';
                }else{
                    this.loadResource();
                }
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        mounted: function(){

        },
        watch: {
            page: function(){
                this.loading = true;
                clearTimeout(this.timeout);
                this.timeout = setTimeout(()=>{
                    this.loadResource();
                }, 400)
            },
            keyword: function(){
                this.loading = true;
                this.page = 0;
                this.has_more_data = true;
                this.data = [];
                clearTimeout(this.timeout);
                this.timeout = setTimeout(()=>{
                    this.loadResource();
                }, 500)
            }
        }
    });

    Vue.component('permissionlist', {
        template: `
            <div class="modal" @click="watchClickOutsite($event)">
                <div class="modal-body animate" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Danh sách thành viên</div>
                    <div class="permission">
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <div class="d-flex">
                                    <input type="text" v-model="form.phone" placeholder="Nhập số điện thoại" />
                                    <button class="btn btn-primary ml-1" @click.stop.prevent="addPermissionAccount($event)">Chia sẻ</button>
                                </div>
                            </div>
                        </div>
                        <div class="items">
                            <template v-if="permissions.length > 0">
                                <table>
                                    <tr>
                                        <th></th>
                                        <th>Thành viên</th>
                                        <th>Xem</th>
                                        <th>Sửa</th>
                                        <th></th>
                                    </tr>
                                    <template v-for="(item, index) in permissions">
                                        <tr>
                                            <td>{{ index+1 }}</td> 
                                            <td>{{ item.phone }}</td>
                                            <td>
                                                <label class="checkbox" style="display:block;margin-top:0px;">
                                                    <input type="checkbox" v-model="item.read" @change="changePermissionState('read', index)" />
                                                    <span></span>
                                                </label>
                                            </td>
                                            <td>
                                                <label class="checkbox" style="display:block;margin-top:0px;">
                                                    <input type="checkbox" v-model="item.edit" @change="changePermissionState('edit', index)" />
                                                    <span></span>
                                                </label>
                                            </td>
                                            <td>
                                                <div @click.stop.prevent="removePhoneToGroup($event, item)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M135.2 17.69C140.6 6.848 151.7 0 163.8 0H284.2C296.3 0 307.4 6.848 312.8 17.69L320 32H416C433.7 32 448 46.33 448 64C448 81.67 433.7 96 416 96H32C14.33 96 0 81.67 0 64C0 46.33 14.33 32 32 32H128L135.2 17.69zM394.8 466.1C393.2 492.3 372.3 512 346.9 512H101.1C75.75 512 54.77 492.3 53.19 466.1L31.1 128H416L394.8 466.1z"/></svg></div>
                                            </td>
                                        </tr>
                                    </template>
                                </table>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                form: {
                    phone: ''
                },
                permissions: [],
                group: null,
                loading: false,
                callback: null
            }
        },
        methods: {
            changePermissionState: function(permission, index){
                let vm = this;
                vm.$root.postData(vm.$root.setting.api_resource.update_phone_permission, {
                    group_id: vm.group.id,
                    phone: vm.permissions[index].phone,
                    permission: permission,
                    status: vm.permissions[index][permission]
                }).then(res => {
                    if(!res.error){
                        
                    }
                });
            },
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            removePhoneToGroup: function(e, item){
                let vm = this;
                vm.$root.showConfirmBox({
                    message: 'Bạn chắc chắn muốn xóa tài khoản này ra khỏi rổ hàng ?',
                    callback: function(confirm){
                        if(confirm){
                            vm.$root.postData(vm.$root.setting.api_resource.remove_phone_from_group, {
                                phone: item.phone,
                                group_id: vm.group.id
                            })
                            .then(res => {
                                vm.loadResource();
                            });
                        }else{
                            vm.loadResource();
                        }
                    }
                })
            },
            addPermissionAccount: function(e){
                let vm = this;
                if(vm.form.phone.length < 9){
                    vm.$root.showMessageBox('Vui lòng nhập đủ số điện thoại');
                    return;
                }

                vm.$root.postData(vm.$root.setting.api_resource.add_phone_to_group, {
                    phone: vm.form.phone,
                    group_id: vm.group.id
                }).then(res => {
                    if(res.error){
                        vm.$root.showMessageBox(res.message);
                    }else{
                        vm.form.phone = '';
                        vm.loadResource();
                    }
                });
            },
            loadResource: function(){
                let vm = this;
                vm.loading = true;
                vm.$root.postData(vm.$root.setting.api_resource.list_group_permission, {
                    group_id: vm.group.id
                }).then(res => {
                    if(!res.error){
                        var permissions = {};
                        for (let index = 0; index < res.data.length; index++) {
                            const element = res.data[index];
                            if(typeof permissions[element.phone] == 'undefined'){
                                permissions[element.phone] = {
                                    phone: element.phone,
                                    read: false,
                                    edit: false
                                }
                            }

                            if(element.permission == 'read'){
                                permissions[element.phone].read = element.status == 0 ? false : true;
                            }

                            if(element.permission == 'edit'){
                                permissions[element.phone].edit = element.status == 0 ? false : true;
                            }
                        }

                        vm.permissions = Object.values(permissions);
                    }
                });
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.callback = option && typeof option.callback == 'function' ? option.callback : null;
                this.group = option && typeof option.group != 'undefined' ? option.group : null;
                this.loadResource();
                this.$el.classList.add('open');
            },
            cancel: function(){
                if(typeof this.callback == 'function'){
                    this.callback(this.permissions.length);
                }
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
                if(typeof this.callback == 'function'){
                    this.callback(this.permissions.length);
                }
            }
        }
    })

    Vue.component('detailgroup', {
        template: `
        <div class="modal modal-center">
            <div class="modal-body animate" ref="modalbody">
                <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="modal-title">Rổ hàng "{{ group ? group.name : '' }}"</div>
                <div class="detailgroup">
                    <div class="quick-search">
                        <div class="icon"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="search" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="svg-inline--fa fa-search fa-w-16 fa-3x"><path fill="currentColor" d="M508.5 481.6l-129-129c-2.3-2.3-5.3-3.5-8.5-3.5h-10.3C395 312 416 262.5 416 208 416 93.1 322.9 0 208 0S0 93.1 0 208s93.1 208 208 208c54.5 0 104-21 141.1-55.2V371c0 3.2 1.3 6.2 3.5 8.5l129 129c4.7 4.7 12.3 4.7 17 0l9.9-9.9c4.7-4.7 4.7-12.3 0-17zM208 384c-97.3 0-176-78.7-176-176S110.7 32 208 32s176 78.7 176 176-78.7 176-176 176z"></path></svg></div>
                        <input type="text" autocomplete="off" v-model="keyword" autofill="off" placeholder="Tìm từ khóa" />
                    </div>
                    <div class="items">
                        <template v-if="data.length > 0">
                            <template v-for="(item, index) in data">
                                <div class="item has-action" @click.stop.prevent="showOption($event, item)">
                                    <div class="name">{{ item.name }}</div>
                                    <div class="note">{{ item.note }}</div>
                                    <div class="remain">Ngày lưu: {{ item.created_at | full-time }}</div>
                                    <div class="attachs">
                                        <div class="image-item" v-for="(image, imgindex) in item.images" v-if="imgindex < 4" v-if="item.images.length" @click.stop.prevent="viewImage(item, imgindex)">
                                            <img :src="image" />
                                            <div class="more-image-item" v-if="item.images.length > 4 && imgindex == 3">
                                                +{{ item.images.length - 4 }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </template>
                            <div class="d-flex btn btn-default" v-if="!loading && has_more_data" @click.stop.prevent="loadMore($event)">Tải thêm dữ liệu</div>
                        </template>
                        <template v-if="data.length == 0 && !loading">
                            <div class="pt-1 pb-1 mt-1 mb-1" style="text-align:center;">{{ keyword != '' ? 'Không tìm thấy kết quả phù hợp' : 'Không tìm thấy danh sách điểm đã lưu' }}</div>
                        </template>

                        <template v-if="loading">
                            <loading_ios></loading_ios>
                        </template>
                    </div>
                </div>
            </div>
        </div>
        `,
        data: function(){
            return {
                group: null,
                loading: false,
                data: [],
                page: 0,
                keyword: '',
                timeout: null,
                has_more_data: true,
                callback: null
            }
        },
        filters: {
            'full-time': function(timestamp){
                timestamp = Number(timestamp);
                // Nếu timestamp là giây, chuyển sang milliseconds
                if (timestamp.toString().length === 10) {
                    timestamp *= 1000;
                }

                const date = new Date(timestamp);

                const dd = String(date.getDate()).padStart(2, '0');
                const mm = String(date.getMonth() + 1).padStart(2, '0'); // Tháng bắt đầu từ 0
                const yyyy = date.getFullYear();

                const hh = String(date.getHours()).padStart(2, '0');
                const ii = String(date.getMinutes()).padStart(2, '0');

                return `${dd}/${mm}/${yyyy} ${hh}:${ii}`;
            }
        },
        methods: {
            loadMore: function(){
                if(this.has_more_data){
                    this.page = this.page + 1;
                }
            },
            showOption: function(event, item){
                let vm = this;

                if(typeof vm.callback == 'function'){
                    vm.callback(item);
                    vm.close();
                    return;
                }

                let selectitems = [
                    {
                        name: 'Xem bản đồ quy hoạch',
                        id: 'viewplan'
                    },
                    {
                        name: 'Xem bảng tọa độ ranh',
                        id: 'viewcooordinate'
                    },
                    {
                        name: 'Cập nhật thông tin',
                        id: 'viewinfo'
                    }
                ];


                if(vm.group.isShared){
                    if(item.hasEditPermission){
                        selectitems.push({
                            name: 'Xóa khỏi rổ hàng',
                            id: 'remove'
                        });
                    }
                }else{
                    selectitems.push({
                        name: 'Xóa khỏi rổ hàng',
                        id: 'remove'
                    });
                }

                vm.$root.$refs.action_sheet.open({
                    items: selectitems,
                    title: 'Chọn thao tác sử dụng',
                    callback: function(e){
                        if(e){
                            switch (e.id) {
                                case 'viewplan':
                                    vm.viewPlanOnMap(item);
                                    break;
                                case 'viewcooordinate':
                                    vm.viewCoordinate(item);
                                    break;
                                case 'viewinfo':
                                    vm.editPoint(item);
                                    break;
                                case 'remove':
                                    vm.removePoint(item);
                                    break;
                                case 'viewimage':
                                    vm.viewImage(item, 0);
                                    break;
                                default:
                                    break;
                            }
                        }
                    }
                });
            },
            viewImage: function(item, index){
                let vm = this;
                vm.$root.$refs.sliderimage.open({
                    images: item.images,
                    index: index
                });
            },
            editPoint: function(item){
                let vm = this;
                vm.$root.$refs.updategroupitem.open({
                    form: {
                        id: item.id,
                        name: item.name,
                        note: item.note,
                        images: item.images
                    },
                    callback: function(newvalue){
                        if(newvalue){
                            let findIndex = vm.data.findIndex( e => e.id == newvalue.id);
                            if(findIndex > -1){
                                vm.data[findIndex].images = newvalue.images;
                                vm.data[findIndex].name = newvalue.name;
                                vm.data[findIndex].note = newvalue.note;
                            }
                        }
                    }
                });
            },
            viewCoordinate: function(item){
                let vm = this;
                let geometry = vm.$root.getItemGeometry(item);

                if(geometry){
                    let centerPoint = vm.$root.getCenterGeometry(geometry);
                    vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                        lng: centerPoint.lng,
                        lat: centerPoint.lat
                    }).then((res)=>{
                        if(!res.error && res.data && res.data.province){
                            let provinces = JSON.parse(JSON.stringify(window.provinces));
                            let province = provinces.find(e => e.id == res.data.province.id);
                            if(province){
                                let mainProvince = province.childs.find(item => item.is_main);
                                if(mainProvince){
                                    vm.$root.reloadC(mainProvince.base_coordinate);

                                    let points = vm.$root.getGeometryCoordinates(geometry);
                                    points = points.map((point)=>{
                                        let lng = point[0];
                                        let lat = point[1];

                                        let vn2000Point = vm.$root.e(atob(vm.$root.b),atob(vm.$root.a)).inverse([lng, lat]);
                                        return {
                                            lng: Number(lng.toFixed(10)),
                                            lat: Number(lat.toFixed(10)),
                                            x: Number(vn2000Point[0].toFixed(3)),
                                            y: Number(vn2000Point[1].toFixed(3))
                                        };
                                    });

                                    vm.$root.$refs.coordinatetable.open({
                                        points: points,
                                        base_coordinate: mainProvince.base_coordinate
                                    });
                                }
                            }
                        }
                    });
                }
            },
            viewPlanOnMap: function(item){
                let vm = this;
                let geometry = vm.$root.getItemGeometry(item);
                if(geometry){
                    let centerPoint = vm.$root.getCenterGeometry(geometry);
                    vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                        lng: centerPoint.lng,
                        lat: centerPoint.lat
                    }).then((res)=>{
                        if(!res.error && res.data && res.data.province){
                            vm.close();
                            vm.$root.$refs.grouplist.close();

                            let provinces = JSON.parse(JSON.stringify(window.provinces));
                            let province = provinces.find(e => e.id == res.data.province.id);
                            if(province){
                                vm.$root.$refs['app-map'].setMap({
                                    ward: res.data.ward,
                                    province: province,
                                    feature: {
                                        type: 'Feature',
                                        geometry: geometry
                                    }
                                });
                            }
                        }else{
                            vm.$root.showMessageBox('Không thể xác định vị trí dựa theo tọa độ của điểm này');
                        }
                    })
                }
            },
            removePoint: function(item){
                let vm = this;
                vm.$root.showConfirmBox({
                    message: 'Bạn chắc chắn muốn xóa điểm này khỏi rổ hàng ?',
                    callback: function(confirm){
                        if(confirm){
                            vm.loading = true;
                            vm.$root.postData(vm.$root.setting.api_resource.v1_remove_item_from_group, {
                                id: item.id
                            })
                            .then(res => {
                                vm.reloadResource();
                            });
                        }else{
                            vm.$el.classList.add('open');
                        }
                    }
                })
            },
            reloadResource: function(){
                this.data = [];
                if(this.page != 0){
                    this.page = 0;
                }else{
                    this.loadResource();
                }
            },
            loadResource: function(){
                let vm = this;
                vm.loading = true;
                vm.$root.postData(vm.$root.setting.api_resource.detail_group_items, {
                    keyword: encodeURIComponent(vm.keyword),
                    page: vm.page,
                    group_id: vm.group.id
                })
                .then(res => {
                    vm.loading = false;

                    res.data.map((item)=>{
                        item.images = item.images != '' ? JSON.parse(item.images) : [];
                        vm.data.push(item);
                    });

                    vm.has_more_data = res.has_more;
                });
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.group = option.group;
                this.$el.classList.add('open');
                this.data = [];

                if(this.page != 0){
                    this.page = 0;
                }else if(this.keyword != ''){
                    this.keyword = '';
                }else{
                    this.loadResource();
                }
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        mounted: function(){
            
        },
        watch: {
            page: function(){
                this.loading = true;
                clearTimeout(this.timeout);
                this.timeout = setTimeout(()=>{
                    this.loadResource();
                }, 400)
            },
            keyword: function(){
                this.loading = true;
                this.page = 0;
                this.has_more_data = true;
                this.data = [];
                clearTimeout(this.timeout);
                this.timeout = setTimeout(()=>{
                    this.loadResource();
                }, 500)
            }
        }
    });

    Vue.component('updategroupitem', {
        template: `
            <div class="modal">
                <div class="modal-body animate" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Cập nhật thông tin</div>
                    <div class="login">
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <label class="sub-title">Tên điểm</label>
                                <input type="text" v-model="form.name" />
                            </div>
                        </div>
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <label class="sub-title">Ghi chú điểm</label>
                                <textarea v-model="form.note"></textarea>
                            </div>
                        </div>
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <label class="sub-title">Ảnh đính kèm</label>
                                <div class="image-uploaded-list">
                                    <div class="item" v-for="(item, index) in form.images">
                                        <img :src="item" />
                                        <div class="remove-image-btn" @click.stop.prevent="removeImage($event, index)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                                    </div>
                                    <div class="item btn-attach-image">
                                        <label for="attach-image">+</label>
                                    </div>
                                </div>
                                <div class="image-list">
                                    <div class="item" v-for="item in images">
                                        <div class="image"><img :src="item.url" /></div>
                                        <div class="size">{{ item.size }}</div>
                                        <div class="status">{{ item.status }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="d-flex">
                            <button class="btn btn-primary flex-1" @click.stop.prevent="update($event)">{{ sending ? 'Đang lưu...' : 'Cập nhật' }}</button>
                        </div>
                        <input id="attach-image" ref="attach_image" type="file" style="display:none;" multiple @change="repairUpload($event)" accept="image/*" />
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                mode: 'view',
                can_edit: false,
                form: {
                    id: '',
                    name: '',
                    note: '',
                    images: []
                },
                callback: null,
                sending: false,
                loading: false,
                images: []
            }
        },
        methods: {
            removeImage: function(e, index){
                let vm = this;
                vm.form.images.splice(index, 1);
            },
            repairUpload: function(e){
                for (let index = 0; index < e.target.files.length; index++) {
                    const element = e.target.files[index];
                    this.images.push({
                        url: URL.createObjectURL(element),
                        size: this.formatBytes(element.size, 2),
                        real_url: '',
                        status: 'Chờ tải'
                    });
                }
            },
            upload: function(fileIndex, callback){
                let vm = this;

                if(typeof vm.images[fileIndex] == 'undefined'){
                    callback();
                }else{
                    vm.images[fileIndex].status = 'Đang tải...';
                    window.resizeImage(vm.images[fileIndex].url).then((image)=>{
                        vm.$root.postFileData(vm.$root.setting.api_resource.upload_group_item_image, {
                            file: image
                        }).then((res)=>{
                            if(!res.error){
                                vm.images[fileIndex].status = 'Hoàn tất';
                                vm.images[fileIndex].real_url = res.data;
                                vm.form.images.push(res.data);
                            }else{
                                vm.images[fileIndex].status = 'Tải thất bại';
                            }

                            setTimeout(()=>{
                                vm.upload(fileIndex + 1, callback);
                            }, 100)
                            
                        }).catch(()=>{
                            vm.images[fileIndex].status = 'Tải thất bại';
                            setTimeout(()=>{
                                vm.upload(fileIndex + 1, callback);
                            }, 100)
                        });
                    });
                }
            },
            formatBytes: function (bytes, decimals) {
                if(bytes == 0) return '0 Bytes';
                var k = 1024,
                    dm = decimals || 2,
                    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
                    i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
            },
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            update: function(){
                let vm = this;
                vm.sending = true;
                vm.upload(0, function(){
                    let form = JSON.parse(JSON.stringify(vm.form));
                    form.name = encodeURIComponent(form.name);
                    form.note = encodeURIComponent(form.note);
                    vm.$root.postData(vm.$root.setting.api_resource.update_group_item, form).then(res => {
                        vm.sending = false;
                        if(!res.error){
                            if(typeof vm.callback == 'function'){
                                vm.callback({
                                    id: vm.form.id,
                                    name: vm.form.name,
                                    note: vm.form.note,
                                    images: vm.form.images
                                });
                                vm.$root.showMessageBox(res.message);
                            }
                        }
                    });
                });
            },
            open: function(option){
                let vm = this;
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;

                vm.can_edit = false;
                vm.mode = 'edit';
                vm.images = [];
                vm.callback = option && typeof option.callback=='function' ? option.callback : null;
                vm.form = option && typeof option.form != 'undefined' ? option.form : {
                    id: '',
                    name: '',
                    note: '',
                    images: []
                };
                vm.loading = true;
                vm.$root.postData(vm.$root.setting.api_resource.detail_item, {
                    id: vm.form.id
                }).then(res => {
                    vm.loading = false;
                    if(!res.error){
                        vm.form.name = res.data.name;
                        vm.form.note = res.data.note;
                        vm.form.images = res.data.images != '' ? JSON.parse(res.data.images) : [];
                        vm.can_edit = res.can_edit;
                        if(!vm.can_edit){
                            vm.$root.showMessageBox("Bạn không có quyền cập nhật thông tin");
                            vm.close();
                        }
                    }else{
                        vm.$root.showMessageBox(res.message);
                    }
                });
                vm.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        }
    }); 

    Vue.component('parcel-properties', {
        props: ['parcel'],
        template: `
        <div class="parcel-properties-box">
            <div class="close-btn" @click.stop.prevent="closeInfoBox()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
            <div class="title">Thông tin thửa</div>
            <div class="properties-scroll-box">
                <div class="items">
                    <template v-for="item in parcel.properties">
                        <div class="item" v-html="item"></div>
                    </template>
                    <!-- Thông tin thêm về QHC -->
                    <template v-for="item in parcel.plan_detail">
                        <div class="item">
                            <div class="label">{{ item.label }}</div>
                            <div class="value">{{ item.value }}</div>
                        </div>
                    </template>
                </div>
                <div class="plan_info">
                    <loading_ios v-if="parcel.is_checking_plan"></loading_ios>
                    <template v-if="!parcel.is_checking_plan">
                        <template v-for="item in parcel.plan_info">
                            <div class="plan-row" :class="item.info && item.info.length > 0 ? 'has-detail' : ''">
                                <div class="plan-area" v-if="item.area">{{ item.area }} m<sup>2</sup></div>
                                <div class="plan-color" v-if="item.plan_type != 'QHC'" :style="'background:' + item.color">{{ item.str_code }}</div>
                                <div class="plan-name" :class="item.plan_type">{{ item.name }}</div>
                                <div class="note-icon" v-if="item.note && item.note != ''">
                                    <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M464 256A208 208 0 1 0 48 256a208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256zm169.8-90.7c7.9-22.3 29.1-37.3 52.8-37.3h58.3c34.9 0 63.1 28.3 63.1 63.1c0 22.6-12.1 43.5-31.7 54.8L280 264.4c-.2 13-10.9 23.6-24 23.6c-13.3 0-24-10.7-24-24V250.5c0-8.6 4.6-16.5 12.1-20.8l44.3-25.4c4.7-2.7 7.6-7.7 7.6-13.1c0-8.4-6.8-15.1-15.1-15.1H222.6c-3.4 0-6.4 2.1-7.5 5.3l-.4 1.2c-4.4 12.5-18.2 19-30.6 14.6s-19-18.2-14.6-30.6l.4-1.2zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/></svg>
                                    <div class="text-hover">{{ item.note }}</div>
                                </div>
                            </div>
                            <div class="detail-plan-row" v-if="item.info && item.info.length > 0">
                                <div class="item" v-for="detail in item.info">
                                    <div class="detail-label">{{ detail.label }}</div>
                                    <div class="detail-value">{{ detail.value }}</div>
                                </div>
                            </div>
                        </template>
                    </template>
                </div>
            </div>
            <label class="checkbox mt-1" v-if="parcel.geometry && parcel.geometry.type != 'Point'">
                <input type="checkbox" v-model="parcel.show_distance" />
                <span>Hiện chiều dài cạnh</span>
            </label>
            <label class="checkbox mt-1">
                <input type="checkbox" v-model="parcel.show_parcel_label" />
                <span>Hiện thửa xung quanh</span>
            </label>
            <div class="d-flex mt-1">
                <div class="btn-sm btn-primary" @click.stop.prevent="savePoint($event)" v-if="$root.u && $root.setting && $root.u.phone != $root.setting.trial_phone">Lưu điểm</div>
                <div class="btn-sm ml-1" :class="$root.u && $root.setting && $root.u.phone != $root.setting.trial_phone ? 'btn-default' : 'btn-primary'" @click.stop.prevent="createShareCode($event)">
                    <template v-if="!share_code_loading">Mã chia sẻ</template>
                    <template v-if="share_code_loading">Đang lấy mã...</template>
                </div>
                <div class="btn-sm btn-default ml-1" @click.stop.prevent="$parent.viewCoordinateParcel($event)">Tọa độ ranh</div>
            </div>
        </div>
        `,
        data: function(){
            return {
                is_expand: true,
                share_code_loading: false
            }
        },
        methods: {
            createShareCode: function(e){
                let vm = this;
                if(!vm.share_code_loading){
                    vm.share_code_loading = true;
                    vm.$root.postData(vm.$root.setting.api_resource.create_sharecode, {
                        geometry: vm.parcel.geometry
                    }).then(res => {
                        vm.share_code_loading = false;
                        if(res.error){
                            vm.$root.showMessageBox(res.message);
                        }else{
                            vm.$root.$refs.sharecode.open({
                                code: res.data.code,
                                expired: res.data.expired
                            });
                        }
                    });
                }
            },
            savePoint: function(e){
                let vm = this;
                let properties = vm.parseProperties(vm.parcel.properties);
                vm.$root.$refs.newpoint.open({
                    form: {
                        name: '',
                        note: typeof properties['Khu vực mới'] ? properties['Khu vực mới'] : '',
                        geometry: vm.parcel.geometry
                    }
                });
            },
            closeInfoBox: function(){
                this.$parent.hideSelectedParcel();
            },
            parseProperties: function(arr) {
                let result = {};
                let parser = new DOMParser();

                arr.forEach(html => {
                    let doc = parser.parseFromString(html, 'text/html');
                    let label = doc.querySelector('.label')?.textContent.trim();
                    let value = doc.querySelector('.value')?.innerText.trim(); // innerText giữ được m²
                    if (label && value) {
                    result[label] = value;
                    }
                });

                return result;
            },
        },
        computed: {

        },
        mounted: function(){

        }
    });

    Vue.component('newpoint', {
        template: `
            <div class="modal modal-center">
                <div class="modal-body animate" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Lưu điểm</div>
                    <div class="login">
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <label class="sub-title">Tên điểm</label>
                                <input type="text" class="mt-05" v-model="form.name" />
                            </div>
                        </div>
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <label class="sub-title">Ghi chú điểm</label>
                                <textarea class="mt-05" v-model="form.note"></textarea>
                            </div>
                        </div>
                        <div class="d-flex">
                            <button class="btn-sm btn-primary mr-1" @click.stop.prevent="save($event)">{{ sending ? 'Đang lưu...' : 'Lưu điểm' }}</button>
                            <button class="btn-sm btn-primary mr-1" @click.stop.prevent="saveToGroup($event)">Lưu vào rổ hàng</button>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                form: {
                    name: '',
                    note: '',
                    geometry: null
                },
                callback: null,
                sending: false
            }
        },
        methods: {
            verifyForm: function(){
                if(this.form.name.trim() == ''){
                    this.$root.showMessageBox("Vui lòng nhập tên điểm cần lưu");
                    return false;
                }

                return true;
            },
            loadAllGroups: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    vm.$root.postData(vm.$root.setting.api_resource.group_list_all, {})
                    .then(res => {
                        resolve(res.data);
                    });
                })
            },
            saveToGroup: function(e){
                let vm = this;
                if(vm.verifyForm()){
                    vm.close();
                    vm.loadAllGroups().then((result)=>{
                        if(result.length > 0){
                            result.push({
                                name: '+ Tạo rổ hàng mới',
                                id: -1
                            });
                            vm.$root.$refs.action_sheet.open({
                                items: result,
                                title: 'Chọn rổ hàng',
                                callback: function(e){
                                    if(e){
                                        if(e.id == -1){
                                            vm.addToNewGroup();
                                        }else{
                                            let newitem = JSON.parse(JSON.stringify(vm.form));
                                            newitem.name = encodeURIComponent(newitem.name);
                                            newitem.note = encodeURIComponent(newitem.note);
                                            newitem.geometry = vm.$root.getItemGeometry(newitem);

                                            vm.$root.postData(vm.$root.setting.api_resource.add_to_group, {
                                                group_id: e.id,
                                                item: newitem
                                            })
                                            .then(res => {
                                                vm.$root.showMessageBox(res.message);
                                            });
                                        }
                                    }
                                }
                            });
                        }else{
                            vm.addToNewGroup();
                        }
                    })
                }
            },
            addToNewGroup: function(){
                let vm = this;
                vm.$root.$refs.addgroup.open({
                    title: 'Tạo mới rổ hàng',
                    callback: function(id){
                        if(id){
                            let newitem = JSON.parse(JSON.stringify(vm.form));
                            newitem.name = encodeURIComponent(newitem.name);
                            newitem.note = encodeURIComponent(newitem.note);
                            newitem.geometry = vm.$root.getItemGeometry(newitem);
                            vm.$root.postData(vm.$root.setting.api_resource.add_to_group, {
                                group_id: id,
                                item: newitem
                            })
                            .then(res => {
                                vm.$root.showMessageBox(res.message);
                            });
                        }
                    }
                })
            },
            save: function(){
                let vm = this;
                if(vm.verifyForm()){
                    vm.sending = true;
                    let form = JSON.parse(JSON.stringify(vm.form));
                    form.name = encodeURIComponent(form.name);
                    form.note = encodeURIComponent(form.note);
                    vm.$root.postData(vm.$root.setting.api_resource.save_point, form).then(res => {
                        vm.sending = false;
                        if(!res.error){
                            vm.$root.showMessageBox(res.message);
                        }
                        vm.close();
                    });
                }
            },
            open: function(option){
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.form = option && typeof option.form != 'undefined' ? option.form : {
                    name: '',
                    note: '',
                    geometry: null
                };

                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            cancel: function(){
                if(typeof this.callback == 'function'){
                    this.callback();
                }
                this.$el.style.removeProperty('z-index');
                this.$el.classList.remove('open');
            },
            close: function() {
                this.$el.style.removeProperty('z-index');
                this.$el.classList.remove('open');
            }
        }
    });

    Vue.component('addgroup', {
        template: `
            <div class="modal modal-center" @click="watchClickOutsite($event)">
                <div class="modal-body animate sm" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close($event)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">{{ title }}</div>
                    <div class="login">
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <input type="text" v-model="form.name" placeholder="Nhập tên rổ hàng" />
                            </div>
                        </div>
                        <div class="d-flex mt-2">
                            <button class="btn btn-primary flex-1" @click.stop.prevent="save()">{{ sending ? 'Đang gửi...' : 'Xác nhận' }}</button>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                title: '',
                form: {
                    id: 0,
                    name: ''
                },
                callback: null,
                sending: false
            }
        },
        methods: {
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            save: function(){
                let vm = this;
                vm.sending = true;
                let form = JSON.parse(JSON.stringify(vm.form));
                form.name = encodeURIComponent(form.name);
                vm.$root.postData(vm.$root.setting.api_resource.save_group, form).then(res => {
                    vm.sending = false;
                    if(!res.error){
                        if(typeof vm.callback == 'function'){
                            vm.callback(res.id, vm.form, res.message);
                        }
                    }
                    vm.close();
                });
            },
            open: function(option){
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                this.title = option && typeof option.title ? option.title : 'Tạo mới rổ hàng';
                this.form = option && typeof option.form != 'undefined' ? option.form : {
                    name: '',
                    id: 0
                };
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            cancel: function(){
                if(typeof this.callback == 'function'){
                    this.callback();
                }
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        }
    })

    Vue.component('coordinatetable', {
        template: `
        <div class="modal" @click="watchClickOutsite($event)">
            <div class="modal-body animate" ref="modalbody">
                <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="modal-title">Bảng tọa độ (VN2000 - {{ base_coordinate }})</div>
                <div class="coordinate-table" style="max-height: 80vh;overflow:auto;">
                    <table>
                        <tr>
                            <th>STT</th>
                            <th>Tọa độ X</th>
                            <th>Tọa độ Y</th>
                        </tr>
                        <tr v-for="(item, index) in points">
                            <td>{{ index+1 }}</td>
                            <td>{{ item.x }}</td>
                            <td>{{ item.y }}</td>
                        </tr>
                    </table>
                    <div class="modal-title mt-1">Bảng tọa độ (Google)</div>
                    <table>
                        <tr>
                            <th>STT</th>
                            <th>Tọa độ lat</th>
                            <th>Tọa độ lng</th>
                        </tr>
                        <tr v-for="(item, index) in points">
                            <td>{{ index+1 }}</td>
                            <td>{{ item.lat }}</td>
                            <td>{{ item.lng }}</td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
        `,
        data: function(){
            return  {
                points: [],
                base_coordinate: null,
                callback: null
            }
        },
        methods: {
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            open: function(option) {
                this.points = typeof option.points != 'undefined' ? option.points : [];
                this.callback = typeof option.callback != 'undefined' ? option.callback : null;
                this.base_coordinate = typeof option.base_coordinate != 'undefined' ? option.base_coordinate : null;
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
                if(typeof this.callback == 'function'){
                    this.callback();
                }
            }
        },
        computed: {
            
        }
    });

    Vue.component('sharecode', {
        template: `
            <div class="modal modal-center" @click="watchClickOutsite($event)">
                <div class="modal-body animate" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Mã chia sẻ</div>
                    <div class="sharecode">
                        <div class="mb-1">Gửi mã này cho bạn bè để cùng xem vị trí. Lưu ý mã chia sẽ có thời hạn là {{ expired | full-time }}. Sau thời gian này mã sẽ không còn hiệu lực.</div>
                        <div class="d-flex mt-1 mb-1">
                            <div class="flex-1 sharecode-text">{{ code }}</div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                code: '',
                expired: null
            }
        },
        filters: {
            'full-time': function(value){
                value = Number(value) * 1000;
                let date = new Date(value);

                const dd = String(date.getDate()).padStart(2, '0');
                const mm = String(date.getMonth() + 1).padStart(2, '0');
                const yyyy = date.getFullYear();

                const hh = String(date.getHours()).padStart(2, '0');
                const min = String(date.getMinutes()).padStart(2, '0');

                return `${dd}/${mm}/${yyyy} ${hh}:${min}`;
            }
        },
        methods: {
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
            open: function(option){
                this.code = typeof option.code != 'undefined' ? option.code : '';
                this.expired = typeof option.expired != 'undefined' ? option.expired : null;
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        watch: {
            
        }
    });

    Vue.component('province-box', {
        template: `
        <div class="province-box">
            <province-level-2 ref="province-level-2" v-if="$root.app_version && $root.app_version.code == 2"></province-level-2>
            <province-level-3 ref="province-level-3" v-if="$root.app_version && $root.app_version.code == 3"></province-level-3>
        </div>
        `
    });

    Vue.component('province-level-3', {
        data: function(){
            return {
                provinces: [],
                districts: [],
                wards: [],
                selected_province: null,
                selected_district: null,
                selected_ward: null,
                keyword: '',
                loading_district: false,
                loading_ward: false,
                nextScreenFeature: null,
                my_location: null
            }
        },
        template: `
            <div class="province-container">
                <div class="close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="province-title">Chọn khu vực tra quy hoạch</div>
                <div class="groupsearch">
                    <div class="quick-search">
                        <div class="icon has-action" v-show="!selected_province"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="search" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="svg-inline--fa fa-search fa-w-16 fa-3x"><path fill="currentColor" d="M508.5 481.6l-129-129c-2.3-2.3-5.3-3.5-8.5-3.5h-10.3C395 312 416 262.5 416 208 416 93.1 322.9 0 208 0S0 93.1 0 208s93.1 208 208 208c54.5 0 104-21 141.1-55.2V371c0 3.2 1.3 6.2 3.5 8.5l129 129c4.7 4.7 12.3 4.7 17 0l9.9-9.9c4.7-4.7 4.7-12.3 0-17zM208 384c-97.3 0-176-78.7-176-176S110.7 32 208 32s176 78.7 176 176-78.7 176-176 176z"></path></svg></div>
                        <div class="icon has-action" v-show="selected_province" @click.stop.prevent="backToParent()"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="chevron-left" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" class="svg-inline--fa fa-chevron-left fa-w-8 fa-3x"><path fill="currentColor" d="M238.475 475.535l7.071-7.07c4.686-4.686 4.686-12.284 0-16.971L50.053 256 245.546 60.506c4.686-4.686 4.686-12.284 0-16.971l-7.071-7.07c-4.686-4.686-12.284-4.686-16.97 0L10.454 247.515c-4.686 4.686-4.686 12.284 0 16.971l211.051 211.05c4.686 4.686 12.284 4.686 16.97-.001z"></path></svg></div>
                        <input v-if="!selected_district" type="text" autocomplete="off" autofill="off" :placeholder="selected_province ? 'Tìm trong ' + selected_province.name : 'Tìm trong tỉnh thành (3 cấp)'" v-model="keyword" />
                        <input v-if="selected_district" type="text" autocomplete="off" autofill="off" :placeholder="'Tìm trong ' + selected_district.name" v-model="keyword" />
                    </div>
                    <div class="group-icons">
                        <div class="icon">
                            <span class="svg-icon" @click.stop.prevent="openShareCodeBox($event)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M40 32C53.25 32 64 42.75 64 56V456C64 469.3 53.25 480 40 480H24C10.75 480 0 469.3 0 456V56C0 42.75 10.75 32 24 32H40zM128 48V464C128 472.8 120.8 480 112 480C103.2 480 96 472.8 96 464V48C96 39.16 103.2 32 112 32C120.8 32 128 39.16 128 48zM200 32C213.3 32 224 42.75 224 56V456C224 469.3 213.3 480 200 480H184C170.7 480 160 469.3 160 456V56C160 42.75 170.7 32 184 32H200zM296 32C309.3 32 320 42.75 320 56V456C320 469.3 309.3 480 296 480H280C266.7 480 256 469.3 256 456V56C256 42.75 266.7 32 280 32H296zM448 56C448 42.75 458.7 32 472 32H488C501.3 32 512 42.75 512 56V456C512 469.3 501.3 480 488 480H472C458.7 480 448 469.3 448 456V56zM384 48C384 39.16 391.2 32 400 32C408.8 32 416 39.16 416 48V464C416 472.8 408.8 480 400 480C391.2 480 384 472.8 384 464V48z"/></svg></span>
                        </div>
                    </div>
                </div>
                <div class="menu">
                    <div class="slide-box">
                        <div class="slide-container level-3" ref="slide_container">
                            <ul class="slide-item">
                                <template v-for="(item, index) in filter_provinces">
                                    <li class="has-action" @click.stop.prevent="selectProvince(item)">{{ item.name }}</li>
                                </template>
                            </ul>
                            <ul class="slide-item">
                                <template v-if="loading_district">
                                    <loading_ios></loading_ios>
                                </template>
                                <template v-if="!loading_district">
                                    <template v-for="(item, index) in filter_districts">
                                        <li class="has-action" @click.stop.prevent="selectDistrict(item)">{{ item.name }}</li>
                                    </template>
                                </template>
                            </ul>
                            <ul class="slide-item">
                                <template v-if="loading_ward">
                                    <loading_ios></loading_ios>
                                </template>
                                <template v-if="!loading_ward">
                                    <template v-for="(item, index) in filter_wards">
                                        <li class="has-action" @click.stop.prevent="selectWard(item)">{{ item.name }}</li>
                                    </template>
                                </template>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `,
        methods: {
            close: function(){
                this.$parent.$el.classList.add('hide');
            },
            setNextScreenFeature: function(f){
                this.nextScreenFeature = f;
            },
            nextMapScreen: function(){
                let vm = this;
                vm.$root.checkExpired().then((is_expired)=>{
                    if(!is_expired){
                        vm.$parent.$parent.setMap({
                            ward: this.selected_ward,
                            province: this.selected_province,
                            feature: vm.nextScreenFeature ? JSON.parse(JSON.stringify(vm.nextScreenFeature)) : null,
                            my_location: this.my_location
                        });
                    }else{
                        vm.$root.showConfirmBox({
                            title: 'Thông báo',
                            message: "Tài khoản của bạn đã hết hạn sử dụng vui lòng thanh toán gia hạn để tiếp tục sử dụng",
                            callback: function(confirm_result){
                                if(confirm_result){
                                    vm.$root.$refs.payment.open({
                                        has_reset: false
                                    });
                                }
                            }
                        });
                    }
                })
            },
            selectWard: function(item){
                let vm = this;
                vm.keyword = '';
                vm.selected_ward = item;
                vm.nextMapScreen();
            },
            selectProvince: function(item){
                let vm = this;
                // Kiểm tra nếu chưa login thì bật khung bắt login
                if(!vm.$root.checkPackage()){
                    vm.$root.$refs.login.open({
                        callback: function(){
                            vm.selectProvince(item);
                        }
                    });
                }else{
                    vm.keyword = '';
                    vm.selected_province = item;
                    vm.$refs.slide_container.style.transform = 'translateX(-275px)';

                    vm.loading_district = true;
                    vm.loadDistricts().then((data)=>{
                        vm.loading_district = false;
                        if(data){
                            vm.districts = data.map((e)=>{
                                e.name_search = window.removeVietnameseTones(e.name);
                                return e;
                            }).sort((a, b)=>{
                                return a.name_search.localeCompare(b.name_search);
                            });
                        }
                    });
                }
            },
            selectDistrict: function(item){
                let vm = this;
                vm.keyword = '';
                vm.selected_district = JSON.parse(JSON.stringify(item));
                vm.$refs.slide_container.style.transform = 'translateX(-550px)';

                vm.loading_ward = true;
                vm.loadWards().then((data)=>{
                    vm.loading_ward = false;
                    if(data){
                        vm.wards = data.map((e)=>{
                            e.name_search = window.removeVietnameseTones(e.name);
                            e.district_id = e.parent_id;
                            e.level = 3;
                            return e;
                        }).sort((a, b)=>{
                            return a.name_search.localeCompare(b.name_search);
                        });
                    }
                });
            },
            loadDistricts: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    vm.$root.postData(vm.$root.setting.api_resource.child_level3, {
                        parent_id: vm.selected_province.id
                    }).then(res => {
                        if(!res.error){
                            resolve(res.data);
                        }else{
                            reject(null);
                        }
                    }).catch((msg)=>{
                        reject(null);
                    });
                });
            },
            loadWards: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    vm.$root.postData(vm.$root.setting.api_resource.child_level3, {
                        parent_id: vm.selected_district.id
                    }).then(res => {
                        if(!res.error){
                            resolve(res.data);
                        }else{
                            reject(null);
                        }
                    }).catch((msg)=>{
                        reject(null);
                    });
                });
            },
            accessPointPosition: function(position){
                let vm = this;
                vm.$root.postData(vm.$root.setting.api_resource.convert_place_id_level_3, {
                    lng: position.lng,
                    lat: position.lat
                }).then((res)=>{
                    if(!res.error && res.data && res.data.province){
                        let province = window.provinces.find(e => e.id == res.data.province.id);
                        if(province){
                            vm.$root.checkExpired().then((is_expired)=>{
                                if(is_expired){
                                    vm.$root.showConfirmBox({
                                        title: 'Thông báo',
                                        message: "Tài khoản của bạn đã hết hạn sử dụng vui lòng thanh toán gia hạn để tiếp tục sử dụng",
                                        callback: function(confirm_result){
                                            if(confirm_result){
                                                vm.$root.$refs.payment.open({
                                                    has_reset: false
                                                });
                                            }
                                        }
                                    });
                                }else{
                                    vm.$parent.$parent.setMap({
                                        ward: res.data.ward,
                                        province: province,
                                        feature: vm.nextScreenFeature ? JSON.parse(JSON.stringify(vm.nextScreenFeature)) : {
                                            type: "Feature",
                                            geometry: {
                                                type: "Point",
                                                coordinates: [position.lng, position.lat]
                                            }
                                        },
                                        my_location: vm.my_location
                                    });

                                    setTimeout(()=>{
                                        vm.nextScreenFeature = null;
                                        vm.my_location = null;
                                    }, 100)
                                }
                            })
                        }
                    }else{
                        vm.$root.showMessageBox('Không thể xác định vị trí dựa theo tọa độ hiện tại của bạn ..');
                    }
                });
            },
            openShareCodeBox: function(event){
                let vm = this;
                vm.$root.$refs.sharecodefind.open({
                    callback: function(result){
                        let feature = {
                            type: "Feature",
                            geometry: result
                        };

                        vm.setNextScreenFeature(feature);
                        var centroid = turf.centroid(feature);

                        vm.accessPointPosition({
                            lng: centroid.geometry.coordinates[0],
                            lat: centroid.geometry.coordinates[1]
                        });
                    }
                });
            },
            backToParent: function(){
                if(this.selected_district){
                    this.selected_district = null;
                    this.selected_ward = null;
                    this.$refs.slide_container.style.transform = 'translateX(-275px)';
                }else{
                    this.selected_province = null;
                    this.selected_district = null;
                    this.selected_ward = null;
                    this.$refs.slide_container.style.transform = 'translateX(0%)';
                }
            },
            loadProvinces: function(){
                let vm = this;
                if(typeof window.provinces != 'undefined'){
                    let provinces = JSON.parse(JSON.stringify(window.provinces));
                    vm.provinces = provinces.reduce((p, item)=>{
                        p = p.concat(item.childs);
                        return p;
                    }, []).map((item)=>{
                        item.name_search = window.removeVietnameseTones(item.name);
                        return item;
                    }).sort((a, b)=>{
                        return a.name_search.localeCompare(b.name_search);
                    });
                }else{
                    vm.$root.postData(vm.$root.setting.api_resource.provinces, {}).then(res => {
                        if(!res.error){
                            let provinces = res.data.reduce((p, item)=>{
                                p = p.concat(item.childs);
                                return p;
                            }, []).map((item)=>{
                                item.name_search = window.removeVietnameseTones(item.name);
                                return item;
                            }).sort((a, b)=>{
                                return a.name_search.localeCompare(b.name_search);
                            });

                            vm.provinces = provinces;

                            window.provinces = res.data.map((item)=>{
                                item.name_search = window.removeVietnameseTones(item.name);
                                return item;
                            }).sort((a, b)=>{
                                return a.name_search.localeCompare(b.name_search);
                            });
                        }
                    }).catch((msg)=>{
                        
                    });
                }
            }
        },
        computed: {
            filter_provinces: function(){
                let findKeyword = window.removeVietnameseTones(this.keyword);
                return this.provinces.filter((item)=>{
                    return item.name_search.indexOf(findKeyword) > -1;
                });
            },
            filter_districts: function(){
                let findKeyword = window.removeVietnameseTones(this.keyword);
                return this.districts.filter((item)=>{
                    return item.name_search.indexOf(findKeyword) > -1;
                });
            },
            filter_wards: function(){
                let findKeyword = window.removeVietnameseTones(this.keyword);
                return this.wards.filter((item)=>{
                    return item.name_search.indexOf(findKeyword) > -1;
                });
            }
        },
        created: function(){
            let vm = this;
            vm.loadProvinces();
        }
    });

    Vue.component('province-level-2', { 
        data: function(){
            return {
                provinces: [],
                wards: [],
                selected_province: null,
                selected_ward: null,
                keyword: '',
                loading_ward: false,
                nextScreenFeature: null,
                my_location: null
            }
        },
        template: `
            <div class="province-container">
                <div class="close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="province-title">Chọn khu vực tra quy hoạch</div>
                <div class="groupsearch">
                    <div class="quick-search">
                        <div class="icon has-action" v-show="!selected_province"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="search" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="svg-inline--fa fa-search fa-w-16 fa-3x"><path fill="currentColor" d="M508.5 481.6l-129-129c-2.3-2.3-5.3-3.5-8.5-3.5h-10.3C395 312 416 262.5 416 208 416 93.1 322.9 0 208 0S0 93.1 0 208s93.1 208 208 208c54.5 0 104-21 141.1-55.2V371c0 3.2 1.3 6.2 3.5 8.5l129 129c4.7 4.7 12.3 4.7 17 0l9.9-9.9c4.7-4.7 4.7-12.3 0-17zM208 384c-97.3 0-176-78.7-176-176S110.7 32 208 32s176 78.7 176 176-78.7 176-176 176z"></path></svg></div>
                        <div class="icon has-action" v-show="selected_province" @click.stop.prevent="backToParent()"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="chevron-left" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512" class="svg-inline--fa fa-chevron-left fa-w-8 fa-3x"><path fill="currentColor" d="M238.475 475.535l7.071-7.07c4.686-4.686 4.686-12.284 0-16.971L50.053 256 245.546 60.506c4.686-4.686 4.686-12.284 0-16.971l-7.071-7.07c-4.686-4.686-12.284-4.686-16.97 0L10.454 247.515c-4.686 4.686-4.686 12.284 0 16.971l211.051 211.05c4.686 4.686 12.284 4.686 16.97-.001z"></path></svg></div>
                        <input type="text" autocomplete="off" autofill="off" :placeholder="selected_province ? 'Tìm trong ' + selected_province.name : 'Tìm trong tỉnh thành (2 cấp)'" v-model="keyword" />
                    </div>
                    <div class="group-icons">
                        <div class="icon">
                            <span class="svg-icon" @click.stop.prevent="openShareCodeBox($event)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M40 32C53.25 32 64 42.75 64 56V456C64 469.3 53.25 480 40 480H24C10.75 480 0 469.3 0 456V56C0 42.75 10.75 32 24 32H40zM128 48V464C128 472.8 120.8 480 112 480C103.2 480 96 472.8 96 464V48C96 39.16 103.2 32 112 32C120.8 32 128 39.16 128 48zM200 32C213.3 32 224 42.75 224 56V456C224 469.3 213.3 480 200 480H184C170.7 480 160 469.3 160 456V56C160 42.75 170.7 32 184 32H200zM296 32C309.3 32 320 42.75 320 56V456C320 469.3 309.3 480 296 480H280C266.7 480 256 469.3 256 456V56C256 42.75 266.7 32 280 32H296zM448 56C448 42.75 458.7 32 472 32H488C501.3 32 512 42.75 512 56V456C512 469.3 501.3 480 488 480H472C458.7 480 448 469.3 448 456V56zM384 48C384 39.16 391.2 32 400 32C408.8 32 416 39.16 416 48V464C416 472.8 408.8 480 400 480C391.2 480 384 472.8 384 464V48z"/></svg></span>
                        </div>
                    </div>
                </div>
                <div class="menu">
                    <div class="slide-box">
                        <div class="slide-container" ref="slide_container">
                            <ul class="slide-item">
                                <template v-for="(item, index) in filter_provinces">
                                    <li class="has-action" @click.stop.prevent="selectProvince(item)">{{ item.name }}</li>
                                </template>
                            </ul>
                            <ul class="slide-item">
                                <template v-if="loading_ward">
                                    <loading_ios></loading_ios>
                                </template>
                                <template v-if="!loading_ward">
                                    <template v-for="(item, index) in filter_wards">
                                        <li class="has-action" @click.stop.prevent="selectWard(item)">{{ item.name }}</li>
                                    </template>
                                </template>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `,
        methods: {
            close: function(){
                this.$parent.$el.classList.add('hide');
            },
            setNextScreenFeature: function(f){
                this.nextScreenFeature = f;
            },
            nextMapScreen: function(){
                let vm = this;
                vm.$root.checkExpired().then((is_expired)=>{
                    if(!is_expired){
                        vm.$parent.$parent.setMap({
                            ward: this.selected_ward,
                            province: this.selected_province,
                            feature: JSON.parse(JSON.stringify(vm.nextScreenFeature)),
                            my_location: this.my_location
                        });

                        setTimeout(()=>{
                            vm.nextScreenFeature = null;
                            vm.my_location = null;
                        }, 100)
                    }else{
                        vm.$root.showConfirmBox({
                            title: 'Thông báo',
                            message: "Tài khoản của bạn đã hết hạn sử dụng vui lòng thanh toán gia hạn để tiếp tục sử dụng",
                            callback: function(confirm_result){
                                if(confirm_result){
                                    vm.$root.$refs.payment.open({
                                        has_reset: false
                                    });
                                }
                            }
                        });
                    }
                });
            },
            selectWard: function(item){
                let vm = this;
                // Kiểm tra nếu chưa login thì bật khung bắt login
                if(!vm.$root.checkPackage()){
                    vm.$root.$refs.login.open({
                        callback: function(){
                            vm.selectWard(item);
                        }
                    });
                }else{
                    vm.keyword = '';
                    vm.selected_ward = item;
                    vm.nextMapScreen();
                }
            },
            selectProvince: function(item, autoSelectWard){
                let vm = this;
                // Kiểm tra nếu chưa login thì bật khung bắt login
                if(!vm.$root.checkPackage()){
                    vm.$root.$refs.login.open({
                        callback: function(){
                            vm.selectProvince(item);
                        }
                    });
                }else{
                    vm.keyword = '';
                    vm.selected_province = item;
                    vm.$refs.slide_container.style.transform = 'translateX(-50%)';

                    vm.loading_ward = true;
                    vm.loadWards().then((data)=>{
                        vm.loading_ward = false;
                        vm.wards = data.map((ward)=>{
                            ward.name_search = window.removeVietnameseTones(ward.name);
                            ward.level = 2;
                            return ward;
                        }).sort((a, b)=>{
                            return a.name_search.localeCompare(b.name_search);
                        });

                        if(autoSelectWard){
                            setTimeout(()=>{
                                let findWard = vm.wards.find(ward => ward.id == autoSelectWard.id);
                                if(findWard){
                                    vm.selectWard(findWard);
                                }
                            }, 300)
                        }
                    });
                }
            },
            loadWards: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    vm.$root.postData(vm.$root.setting.api_resource.child_level2, {
                        province_code: vm.selected_province.code
                    }).then(res => {
                        if(!res.error){
                            resolve(res.data);
                        }else{
                            reject(res.message);
                        }
                    }).catch((msg)=>{
                        reject(msg);
                    });
                });
            },
            accessPointPosition: function(position){
                let vm = this;
                vm.$root.postData(vm.$root.setting.api_resource.convert_place_id, {
                    lng: position.lng,
                    lat: position.lat
                }).then((res)=>{
                    if(!res.error && res.data && res.data.province){
                        let province = window.provinces.find(e => e.id == res.data.province.id);
                        if(province){
                            res.data.ward.level = 2;
                            vm.$root.checkExpired().then((is_expired)=>{
                                if(is_expired){
                                    vm.$root.showConfirmBox({
                                        title: 'Thông báo',
                                        message: "Tài khoản của bạn đã hết hạn sử dụng vui lòng thanh toán gia hạn để tiếp tục sử dụng",
                                        callback: function(confirm_result){
                                            if(confirm_result){
                                                vm.$root.nextScreen('payment', {
                                                    has_reset: false
                                                });
                                            }
                                        }
                                    });
                                }else{
                                    vm.$parent.$parent.setMap({
                                        ward: res.data.ward,
                                        province: province,
                                        feature: vm.nextScreenFeature ? JSON.parse(JSON.stringify(vm.nextScreenFeature)) : {
                                            type: "Feature",
                                            geometry: {
                                                type: "Point",
                                                coordinates: [position.lng, position.lat]
                                            }
                                        },
                                        my_location: this.my_location
                                    });

                                    setTimeout(()=>{
                                        vm.nextScreenFeature = null;
                                        vm.my_location = null;
                                    }, 100)
                                }
                            });
                        }
                    }else{
                        vm.$root.showMessageBox('Không thể xác định vị trí dựa theo tọa độ hiện tại của bạn ...');
                    }
                })
            },
            viewPlanByCurrentLocation: function(e){
                let vm = this;
                window.bridge.call('getCurrentLocation', {}, function(position){
                    if(typeof position == 'object'){
                        vm.my_location = position;
                        vm.accessPointPosition(position);
                    }    
                });
            },
            openShareCodeBox: function(event){
                let vm = this;
                vm.$root.$refs.sharecodefind.open({
                    callback: function(result){

                        let feature = {
                            type: "Feature",
                            geometry: result
                        };

                        vm.setNextScreenFeature(feature);
                        var centroid = turf.centroid(feature);

                        vm.accessPointPosition({
                            lng: centroid.geometry.coordinates[0],
                            lat: centroid.geometry.coordinates[1]
                        });
                    }
                });
            },
            backToParent: function(){
                this.selected_province = null;
                this.selected_ward = null;
                this.$refs.slide_container.style.transform = 'translateX(0%)';
            },
            loadProvinces: function(){
                let vm = this;
                if(typeof window.provinces != 'undefined'){
                    vm.provinces = JSON.parse(JSON.stringify(window.provinces));
                }else{
                    vm.$root.postData(vm.$root.setting.api_resource.provinces, {}).then(res => {
                        if(!res.error){
                            let provinces = res.data.map((item)=>{
                                item.name_search = window.removeVietnameseTones(item.name);
                                return item;
                            }).sort((a, b)=>{
                                return a.name_search.localeCompare(b.name_search);
                            });

                            vm.provinces = provinces;
                            window.provinces = provinces;
                        }
                    }).catch((msg)=>{
                        
                    });
                }
            }
        },
        computed: {
            filter_provinces: function(){
                let findKeyword = window.removeVietnameseTones(this.keyword);
                return this.provinces.filter((item)=>{
                    return item.name_search.indexOf(findKeyword) > -1;
                });
            },
            filter_wards: function(){
                let findKeyword = window.removeVietnameseTones(this.keyword);
                return this.wards.filter((item)=>{
                    return item.name_search.indexOf(findKeyword) > -1;
                });
            }
        },
        created: function(){
            let vm = this;
            vm.loadProvinces();
        }
    });

    Vue.component('sharecodefind', {
        template: `
            <div class="modal modal-center">
                <div class="modal-body animate" ref="modalbody">
                    <div class="modal-close-btn" @click.stop.prevent="close($event)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Mã chia sẻ</div>
                    <div class="sharecode">
                        <div class="mb-1">Nhập mã chia sẻ mà bạn được chia sẻ vào khung dưới đây và nhấn xác nhận để tiếp tục</div>
                        <div class="otpform">
                            <input type="text" ref="code" v-model="code" inputmode="decimal" />
                        </div>
                        <div v-if="message != ''" class="mt-1 text-danger">{{ message }}</div>
                        <div class="d-flex mt-1">
                            <button class="btn btn-primary mr-1 mt-1 flex-1" :disabled="code.length < 6 || checking" @click.stop.prevent="apply($event)">{{ checking ? 'Đang kiểm tra...' : 'Kiểm tra' }}</button>
                            <button class="btn btn-default mt-1 flex-1" @click.stop.prevent="close($event)">Hủy bỏ</button>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                code: '',
                checking: false,
                message: '',
                callback: null
            }
        },
        methods: {
            checkShareCode: function(){
                let vm = this;
                vm.message = '';
                vm.checking = true;
                vm.$root.postData(vm.$root.setting.api_resource.check_sharecode, {
                    code: vm.code
                }).then(result => {
                    vm.checking = false;
                    if(result.error == false){
                        if(typeof vm.callback == 'function' && vm.code.trim() != ''){
                            vm.callback(JSON.parse(result.data));
                        }
                        vm.close();
                    }else{
                        vm.message = result.message;
                    }
                });
            },
            apply: function(e){
                this.checkShareCode();
            },
            open: function(option){
                if(this.$root.checkPackage()){
                    this.callback = typeof option.callback == 'function' ? option.callback : null;
                    this.code = '';
                    const totalOpened = document.querySelectorAll('.modal.open').length;
                    this.$el.style.zIndex = 99993 + totalOpened;
                    this.$el.classList.add('open');
                    setTimeout(()=>{
                        this.$refs.code.focus();
                    }, 200)
                    
                }else{
                    let vm = this;
                    vm.$root.$refs.login.open({
                        callback: function(){
                            vm.open(option);
                        }
                    });
                }
            },
            close: function(e) {
                this.$el.classList.remove('open');
                this.callback = null;
                this.$el.style.removeProperty('z-index');
            }
        },
        watch: {
            
        }
    });

    Vue.component('colorlist', {
        template: `
        <div class="modal modal-center">
            <div class="modal-body animate" ref="modalbody">
                <div class="modal-close-btn" @click.stop.prevent="close($event)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="modal-title">Chú giải mã màu</div>
                <div class="color-list">
                    <div class="tab">
                        <div class="item" :class="current_tab == 'sdd' ? 'active' : ''" @click.stop.prevent="current_tab = 'sdd'">Q.Hoạch sử dụng đất</div>
                        <div class="item" :class="current_tab == 'xd' ? 'active' : ''" @click.stop.prevent="current_tab = 'xd'">Q.Hoạch xây dựng</div>
                    </div>
                    <template v-if="current_tab == 'sdd'">
                        <div class="quick-search">
                            <div class="icon"><svg aria-hidden="true" focusable="false" data-prefix="fal" data-icon="search" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="svg-inline--fa fa-search fa-w-16 fa-3x"><path fill="currentColor" d="M508.5 481.6l-129-129c-2.3-2.3-5.3-3.5-8.5-3.5h-10.3C395 312 416 262.5 416 208 416 93.1 322.9 0 208 0S0 93.1 0 208s93.1 208 208 208c54.5 0 104-21 141.1-55.2V371c0 3.2 1.3 6.2 3.5 8.5l129 129c4.7 4.7 12.3 4.7 17 0l9.9-9.9c4.7-4.7 4.7-12.3 0-17zM208 384c-97.3 0-176-78.7-176-176S110.7 32 208 32s176 78.7 176 176-78.7 176-176 176z"></path></svg></div>
                            <input type="text" autocomplete="off" autofill="off" placeholder="Tìm mã loại đất" v-model="keyword" />
                        </div>
                        <div class="items">
                            <div class="item" v-for="(item, index) in colors_filter">
                                <div class="color-item" :style="'background:'+item.color"></div>
                                <div class="color-code">{{ item.code }}</div>
                                <div class="color-name">{{ item.name }}</div>
                            </div>
                        </div>
                    </template>
                    <template v-if="current_tab == 'xd'">
                        <div class="items no-search-box">
                            <div class="item" v-for="(item, index) in symbol_xd">
                                <div class="line-item">
                                    <span v-if="!item.img" :style="'border-bottom:' + item.border_width + ' ' + item.border_type + ' ' + item.color"></span>
                                    <img v-if="item.img" :src="item.img" />
                                </div>
                                <div class="color-name" style="margin-left:20px;">{{ item.name }}</div>
                            </div>
                            <div class="item" v-for="(item, index) in colors_xd">
                                <div class="color-item" :style="'background:'+item.color"></div>
                                <div class="color-code">{{ item.code }}</div>
                                <div class="color-name" style="margin-left:20px;">{{ item.name }}</div>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </div>
        `,
        data: function(){
            return  {
                current_tab: 'sdd',
                keyword: '',
                colors_sdd: [{"name":"Đất sông ngòi, kênh, rạch, suối","code":"SON","color":"rgba(160,255,255,1)"},{"name":"Đất có mặt nước chuyên dùng","code":"MNC","color":"rgba(180,255,255,1)"},{"name":"Đất thủy lợi","code":"DTL","color":"rgba(170,255,255,1)"},{"name":"Đất nuôi trồng thuỷ sản","code":"NTS","color":"rgba(170,255,255,1)"},{"name":"Đất có mặt nước ven biển (quan sát)","code":"MVB","color":"rgba(180,255,255,1)"},{"name":"Đất mặt nước ven biển nuôi trồng thủy sản","code":"MVT","color":"rgba(180,255,255,1)"},{"name":"Đất mặt nước ven biển có rừng","code":"MVR","color":"rgba(180,255,255,1)"},{"name":"Đất mặt nước ven biển có mục đích khác","code":"MVK","color":"rgba(180,255,255,1)"},{"name":"Đất nông nghiệp","code":"NNP","color":"rgba(255,255,100,1)"},{"name":"Đất sản xuất nông nghiệp","code":"SXN","color":"rgba(255,252,110,1)"},{"name":"Đất trồng cây hàng năm","code":"CHN","color":"rgba(255,252,120,1)"},{"name":"Đất trồng lúa","code":"LUA","color":"rgba(255,252,130,1)"},{"name":"Đất chuyên trồng lúa nước","code":"LUC","color":"rgba(255,252,140,1)"},{"name":"Đất trồng lúa nước còn lại","code":"LUK","color":"rgba(255,252,150,1)"},{"name":"Đất trồng lúa nương","code":"LUN","color":"rgba(255,252,180,1)"},{"name":"Đất trồng cây hàng năm khác","code":"HNK","color":"rgba(255,240,180,1)"},{"name":"Đất bằng trồng cây hàng năm khác","code":"BHK","color":"rgba(255,240,180,1)"},{"name":"Đất nương rẫy trồng cây hàng năm khác","code":"NHK","color":"rgba(255,240,180,1)"},{"name":"Đất trồng cây lâu năm","code":"CLN","color":"rgba(255,210,160,1)"},{"name":"Đất lâm nghiệp","code":"LNP","color":"rgba(170,255,50,1)"},{"name":"Đất rừng sản xuất","code":"RSX","color":"rgba(180,255,180,1)"},{"name":"Đất có rừng tự nhiên sản xuất","code":"RSN","color":"rgba(180,255,180,1)"},{"name":"Đất có rừng trồng sản xuất","code":"RST","color":"rgba(180,255,180,1)"},{"name":"Đất trồng rừng sản xuất","code":"RSM","color":"rgba(180,255,180,1)"},{"name":"Đất rừng phòng hộ","code":"RPH","color":"rgba(190,255,30,1)"},{"name":"Đất có rừng tự nhiên phòng hộ","code":"RPN","color":"rgba(190,255,30,1)"},{"name":"Đất có rừng trồng phòng hộ","code":"RPT","color":"rgba(190,255,30,1)"},{"name":"Đất trồng rừng phòng hộ","code":"RPM","color":"rgba(190,255,30,1)"},{"name":"Đất rừng đặc dụng","code":"RDD","color":"rgba(110,255,100,1)"},{"name":"Đất có rừng tự nhiên đặc dụng","code":"RDN","color":"rgba(110,255,100,1)"},{"name":"Đất có rừng trồng đặc dụng","code":"RDT","color":"rgba(110,255,100,1)"},{"name":"Đất trồng rừng đặc dụng","code":"RDM","color":"rgba(110,255,100,1)"},{"name":"Đất làm muối","code":"LMU","color":"rgba(0,0,0,1)"},{"name":"Đất nông nghiệp khác","code":"NKH","color":"rgba(245,255,180,1)"},{"name":"Đất ở","code":"OTC","color":"rgba(255,180,255,1)"},{"name":"Đất ở tại nông thôn","code":"ONT","color":"rgba(255,208,255,1)"},{"name":"Đất ở tại đô thị","code":"ODT","color":"rgba(255,160,255,1)"},{"name":"Đất chuyên dùng","code":"CDG","color":"rgba(255,160,170,1)"},{"name":"Đất trụ sở cơ quan","code":"TSC","color":"rgba(255,170,160,1)"},{"name":"Đất quốc phòng","code":"CQP","color":"rgba(255,100,80,1)"},{"name":"Đất an ninh","code":"CAN","color":"rgba(255,80,70,1)"},{"name":"Đất sản xuất, kinh doanh phi nông nghiệp","code":"CSK","color":"rgba(255,170,160,1)"},{"name":"Đất khu công nghiệp","code":"SKK","color":"rgba(255,170,160,1)"},{"name":"Đất cơ sở sản xuất, kinh doanh","code":"SKC","color":"rgba(255,170,160,1)"},{"name":"Đất cho hoạt động khoáng sản","code":"SKS","color":"rgba(205,170,205,1)"},{"name":"Đất sản xuất vật liệu xây dựng, làm đồ gốm","code":"SKX","color":"rgba(205,170,205,1)"},{"name":"Đất có mục đích công cộng","code":"CCC","color":"rgba(255,170,160,1)"},{"name":"Đất giao thông","code":"DGT","color":"rgba(255,170,50,1)"},{"name":"Đất công trình năng lượng","code":"DNL","color":"rgba(255,170,160,1)"},{"name":"Đất công trình bưu chính viễn thông","code":"DBV","color":"rgba(255,170,160,1)"},{"name":"Đất cơ sở văn hóa","code":"DVH","color":"rgba(255,170,160,1)"},{"name":"Đất cơ sở y tế","code":"DYT","color":"rgba(255,170,160,1)"},{"name":"Đất cơ sở giáo dục ","code":"DGD","color":"rgba(255,170,160,1)"},{"name":"Đất cơ sở thể dục ","code":"DTT","color":"rgba(255,170,160,1)"},{"name":"Đất cơ sở nghiên cứu khoa học","code":"DKH","color":"rgba(255,170,160,1)"},{"name":"Đất cơ sở dịch vụ về xã hội","code":"DXH","color":"rgba(255,170,160,1)"},{"name":"Đất chợ","code":"DCH","color":"rgba(255,170,160,1)"},{"name":"Đất có di tích, danh thắng","code":"DDT","color":"rgba(255,170,160,1)"},{"name":"Đất bãi thải, xử lý chất thải","code":"DRA","color":"rgba(255,170,205,1)"},{"name":"Đất tôn giáo","code":"TON","color":"rgba(255,170,160,1)"},{"name":"Đất tín ngưỡng","code":"TIN","color":"rgba(255,170,160,1)"},{"name":"Đất nghĩa trang, nghĩa địa","code":"NTD","color":"rgba(210,210,210,1)"},{"name":"Đất phi nông nghiệp khác","code":"PNK","color":"rgba(255,170,160,1)"},{"name":"Đất chưa sử dụng","code":"CSD","color":"rgba(255,255,254,1)"},{"name":"Đất bằng chưa sử dụng","code":"BCS","color":"rgba(255,255,254,1)"},{"name":"Đất đồi núi chưa sử dụng","code":"DCS","color":"rgba(255,255,254,1)"},{"name":"Núi đá không có rừng cây","code":"NCS","color":"rgba(230,230,200,1)"},{"name":"Đất xây dựng công trình sự nghiệp","code":"DSN","color":"rgba(255,160,170,1)"},{"name":"Đất xây dựng trụ sở của tổ chức sự nghiệp","code":"DTS","color":"rgba(255,170,160,1)"},{"name":"Đất xây dựng cơ sở ngoại giao","code":"DNG","color":"rgba(255,170,160,1)"},{"name":"Đất xây dựng công trình sự nghiệp khác","code":"DSK","color":"rgba(255,170,160,1)"},{"name":"Đất cụm công nghiệp","code":"SKN","color":"rgba(255,170,160,1)"},{"name":"Đất khu chế xuất","code":"SKT","color":"rgba(255,170,160,1)"},{"name":"Đất thương mại, dịch vụ","code":"TMD","color":"rgba(255,170,160,1)"},{"name":"Đất danh lam thắng cảnh","code":"DDL","color":"rgba(255,170,160,1)"},{"name":"Đất sinh hoạt cộng đồng","code":"DSH","color":"rgba(255,170,160,1)"},{"name":"Đất khu vui chơi, giải trí công cộng","code":"DKV","color":"rgba(255,170,160,1)"},{"name":"Đất công trình công cộng khác","code":"DCK","color":"rgba(255,170,160,1)"}],
                symbol_xd: [
                    {"name":"Ranh giới dự án quy hoạch","color":"rgb(63, 72, 204)","border_type":"dashed","border_width":"2px"},
                    {"name":"Ranh giới kiến trúc","color":"rgb(255, 127, 38)","border_type":"dashed","border_width":"2px"},
                    {"name":"Lòng đường","color":"rgb(250, 52, 17)","border_type":"dashed","border_width":"2px"},
                    {"name":"Lề đường","color":"rgb(0, 255, 197)","border_type":"dashed","border_width":"2px"},
                    {"name":"Tim đường","img":"https://qhviet.com/assets/images/timduong.jpg"},
                    {"name":"Đường sắt","img":"https://qhviet.com/assets/images/duongsat.jpg"},
                ],
                colors_xd_v1: [
                    {"name":"Đất công cộng thành phố","color":"rgb(255, 0, 0)"},
                    {"name":"Đất cây xanh công viên, TDTT Thành phố","color":"rgb(82, 165, 0)"},
                    {"name":"Đường, quảng trường, nhà ga và bến - bãi đỗ xe Thành phố","color":"rgb(128, 128, 128)"},
                    {"name":"Đất công cộng khu ở Trường phổ thông trung học, TT đào tạo, dạy nghề","color":"rgb(127, 31, 0)"},
                    {"name":"Đất cây xanh, TDTT khu ở","color":"rgb(52, 104, 0)"},
                    {"name":"Đường phố, điểm đổ - dừng xe khu ở","color":"rgb(68, 0, 0)"},
                    {"name":"Đất công cộng đơn vị ở","color":"rgb(255, 0, 0)"},
                    {"name":"Đất cây xanh TDTT mặt nước đơn vị ở","color":"rgb(52, 104, 0)"},
                    {"name":"Đất trường Tiểu học, THCS, mầm non","color":"rgb(127, 63, 63)"},
                    {"name":"Đất nhóm nhà ở liền kề, nhà ở riêng lẻ","color":"rgb(225, 127, 0)"},
                    {"name":"Đất đường nội bộ dự kiến","color":"rgb(119, 119, 119)"},
                    {"name":"Đất ở thuần","color":"rgb(204, 204, 153)"},
                    {"name":"Đất bãi đỗ xe đơn vị ở dự kiến","color":"rgb(255, 255, 204)"},
                    {"name":"Đất viện nghiên cứu","color":"rgb(0, 95, 127)"},
                    {"name":"Đất tôn giáo - tín ngưỡng","color":"rgb(76, 0, 0)"},
                    {"name":"Đất công nghiệp, kho tàng","color":"rgb(82, 0, 165)"},
                    {"name":"Đất du lịch, nghỉ dưỡng","color":"rgb(255, 0, 255)"},
                    {"name":"Đất an ninh, quốc phòng","color":"rgb(33, 38, 19)"},
                    {"name":"Đất nghĩa trang","color":"rgb(101, 101, 101)"},
                    {"name":"Đất lâm nghiệp, nông nghiệp, đồi núi, mặt nước","color":"rgb(0, 255, 0)"},
                    {"name":"Đất đồi núi","color":"rgb(153, 102, 51)"},
                    {"name":"Đất hoa màu","color":"rgb(255, 102, 153)"},
                    {"name":"Đất làng nghề","color":"rgb(153, 102, 102)"},
                    {"name":"Đất dự trữ phát triển","color":"rgb(255, 153, 255)"},
                    {"name":"Đất cây xanh cách ly, hành lang thoát lũ","color":"rgb(0, 76, 57)"},
                    {"name":"Đầu mối hạ tầng, kỹ thuật","color":"rgb(95, 63, 127)"},
                    {"name":"Đất nhóm nhà ở chung cư","color":"rgb(225, 191, 0)"},
                    {"name":"Đất xử lý nước thải (màu dựa trên bản vẽ quy hoạch)","color":"rgb(212, 170, 255)"}
                ],
                colors_xd: [
                    {"name": "Đất giao thông","code": "DGT","color": "rgb(210, 210, 210)"},{"name": "Đất sông, kênh mương, hồ thủy lợi, thủy điện","code": "SON","color": "rgb(127, 191, 255)"},{"name": "Đất trung tâm y tế","code": "DYT","color": "rgb(254, 50, 50)"},{"name": "Đất giáo dục","code": "DGD","color": "rgb(255, 120, 71)"},{"name": "Đất an ninh quốc phòng","code": "DAN","color": "rgb(189, 81, 126)"},{"name": "Đất công trình đầu mối hạ tầng kỹ thuật","code": "DHT","color": "rgb(226, 121, 70)"},{"name": "Đất khu dân cư","code": "KDC","color": "rgb(205, 170, 101)"},{"name": "Đất cơ sở sản xuất kinh doanh","code": "SKC","color": "rgb(152, 89, 147)"},{"name": "Đất công trình công cộng","code": "CTC","color": "rgb(0, 51, 1)"},{"name": "Đất dự án quy hoạch","code": "DAQ","color": "rgb(246, 121, 121)"},{"name": "Đất khác","code": "DKH","color": "rgb(216, 157, 160)"},{"name": "Đất trung tâm đô thị","code": "KDT","color": "rgb(255, 208, 132)"},{"name": "Đất làng đô thị hóa","code": "DTH","color": "rgb(253, 181, 181)"},{"name": "Đất nhà ở chia lô","code": "OCL","color": "rgb(215, 174, 149)"},{"name": "Đất nhà ở vườn","code": "NOV","color": "rgb(169, 100, 0)"},{"name": "Đất ở cao tầng kết hợp công trình dịch vụ đô thị","code": "CTD","color": "rgb(190, 130, 91)"},{"name": "Đất ở hiện hữu tự điều chỉnh, cải tạo, chỉnh trang","code": "ODC","color": "rgb(240, 159, 101)"},{"name": "Đất ở làng nghề","code": "KON","color": "rgb(180, 120, 111)"},{"name": "Đất ở mật độ trung bình","code": "OTB","color": "rgb(220, 179, 129)"},{"name": "Đất ở tự điều chỉnh","code": "TDC","color": "rgb(189, 149, 149)"},{"name": "Đất Golf, giải trí","code": "DKV","color": "rgb(200, 255, 200)"},{"name": "Đất trường đua","code": "TDU","color": "rgb(119, 101, 100)"},{"name": "Đất văn hóa","code": "DVH","color": "rgb(236, 145, 146)"},{"name": "Đất khu đô thị hiện hữu","code": "DTC","color": "rgb(205, 205, 103)"},{"name": "Đất chưa sử dụng","code": "CSD","color": "rgb(255, 114, 225)"},{"name": "Đất ở nhà phố cải tạo","code": "ONC","color": "rgb(255, 199, 90)"},{"name": "Đường sắt","code": "DDS","color": "rgb(170, 170, 170)"},{"name": "Đất ở mới thấp tầng","code": "OTT","color": "rgb(255, 150, 0)"},{"name": "Đất ở dự án","code": "ODA","color": "rgb(253, 100, 0)"},{"name": "Đất nuôi trồng thủy sản tập trung","code": "NTS","color": "rgb(61, 140, 255)"},{"name": "Đất bến xe, bến bãi, đậu xe, ga","code": "BDX","color": "rgb(79, 80, 129)"},{"name": "Đất kho bãi","code": "DKB","color": "rgb(69, 60, 69)"},{"name": "Đất trồng lúa","code": "LUA","color": "rgb(0, 200, 128)"},{"name": "Đất trồng cây lâu năm","code": "CLN","color": "rgb(9, 149, 120)"},{"name": "Đất trồng cây hằng năm","code": "HNK","color": "rgb(69, 200, 0)"},{"name": "Đất bãi thải, xử lý chất thải","code": "DRA","color": "rgb(50, 50, 50)"},{"name": "Đất di tích thắng cảnh","code": "DDT","color": "rgb(236, 188, 134)"},{"name": "Đất làm muối","code": "LMU","color": "rgb(4, 89, 229)"},{"name": "Đất nông nghiệp khác","code": "NNK","color": "rgb(189, 255, 64)"},{"name": "Đất phi nông nghiệp khác","code": "PNK","color": "rgb(229, 250, 150)"},{"name": "Đất rừng đặc trưng","code": "RDT","color": "rgb(69, 121, 0)"},{"name": "Đất rừng phòng hộ","code": "RPH","color": "rgb(66, 129, 89)"},{"name": "Đất rừng sản xuất","code": "RSX","color": "rgb(0, 121, 80)"},{"name": "Đất sản xuất vật liệu xây dựng, gốm sứ","code": "SKX","color": "rgb(179, 159, 239)"},{"name": "Đất ở thuần","code": "ONT","color": "rgb(169, 189, 150)"},{"name": "Đất bãi bồi ven sông","code": "DCH","color": "rgb(119, 170, 245)"},{"name": "Đất canh tác hỗn hợp","code": "CHH","color": "rgb(0, 255, 0)"},{"name": "Đất ở mật độ cao","code": "OMC","color": "rgb(130, 111, 49)"},{"name": "Đất cho hoạt động khoán sản","code": "SKS","color": "rgb(255, 200, 230)"},{"name": "Đất chăn nuôi","code": "COC","color": "rgb(3, 100, 2)"},{"name": "Đất chưa quy hoạch","code": "CQH","color": "rgb(91, 136, 67)"},{"name": "Đất ở cao tầng","code": "OCT","color": "rgb(137, 113, 68)"},{"name": "Đất xã hội","code": "DXH","color": "rgb(204, 76, 79)"},{"name": "Đất công nghiệp khác","code": "CNK","color": "rgb(56, 167, 1)"},{"name": "Đất ở mật độ thấp","code": "MDT","color": "rgb(201, 150, 50)"},{"name": "Đất bệnh viện","code": "DBV","color": "rgb(255, 79, 121)"},{"name": "Hành lang bảo vệ","code": "HLA","color": "rgb(198, 229, 255)"},{"name": "Đất nhà ở liên kể xây mới","code": "OLK","color": "rgb(200, 214, 151)"},{"name": "Đất ở thương mại, dịch vụ","code": "OTD","color": "rgb(215, 214, 149)"},{"name": "Đất cơ quan","code": "TSC","color": "rgb(199, 100, 4)"},{"name": "Đất công nghiệp","code": "KCN","color": "rgb(203, 102, 153)"},{"name": "Đất thương mại, dịch vụ, du lịch","code": "TMD","color": "rgb(149, 90, 90)"},{"name": "Đất nghĩa trang","code": "NTD","color": "rgb(100, 60, 139)"},{"name": "Đất ở chung cư","code": "OCC","color": "rgb(214, 199, 159)"},{"name": "Đất ở liền kể","code": "OPT","color": "rgb(167, 169, 0)"},{"name": "Đất biệt thự","code": "NVB","color": "rgb(254, 200, 199)"},{"name": "Đất tôn giáo, di tích","code": "TON","color": "rgb(99, 61, 101)"},{"name": "Mặt nước","code": "MNC","color": "rgb(114, 219, 255)"},{"name": "Đất cây xanh đô thị","code": "DCX","color": "rgb(211, 254, 189)"},{"name": "Đất trung tâm thể dục thể thao","code": "DTT","color": "rgb(164, 254, 115)"},{"name": "Đất ở hỗn hợp","code": "OHH","color": "rgb(253, 215, 220)"},{"name": "Đất ở làng xóm","code": "OLX","color": "rgb(90, 108, 82)"},{"name": "Đất công cộng đơn vị ở","code": "CVO","color": "rgb(243, 190, 192)"},{"name": "Đất trường THPT","code": "THP","color": "rgb(255, 120, 70)"},{"name": "Đất trường THCS, tiểu học, mầm non","code": "THT","color": "rgb(255, 120, 71)"},{"name": "Đất đơn vị ở","code": "DVO","color": "rgb(186, 252, 221)"},{"name": "Đất kho tàng","code": "DKT","color": "rgb(243, 251, 183)"},{"name": "Đất trung tâm nghiên cứu, đào tạo","code": "NCD","color": "rgb(241, 173, 141)"},{"name": "Đất cây xanh chuyên đề","code": "CXC","color": "rgb(211, 254, 189)"},{"name": "Đất cây xanh cách ly","code": "CXL","color": "rgb(211, 254, 189)"},{"name": "Đất nông nghiệp","code": "DNN","color": "rgb(209, 252, 245)"},{"name": "Đất lâm nghiệp","code": "DLN","color": "rgb(138, 205, 102)"},{"name": "Đất ở hỗn hợp kết hợp công trình dịch vụ đô thị","code": "HCD","color": "rgb(230, 200, 4)"},{"name": "Đường phố, điểm đổ - dừng xe khu ở","code": "DDD","color": "rgb(68, 0, 0)"},{"name": "Đất công cộng khu ở Trường phổ thông trung học, TT đào tạo, dạy nghề","code": "CTP","color": "rgb(125, 31, 0)"},{"name": "Đất ở dự kiến","code": "ODK","color": "rgb(205, 204, 153)"},{"name": "Đất dự trữ phát triển","code": "DTP","color": "rgb(255, 153, 255)"},{"name": "Đất đường nội bộ dự kiến","code": "DNB","color": "rgb(119, 119, 119)"},{"name": "Đất đồi núi","code": "DDN","color": "rgb(152, 102, 51)"},{"name": "Đất lâm nghiệp, nông nghiệp, đồi núi, mặt nước","code": "DDK","color": "rgb(0, 255, 0)"},{"name": "Đất nhóm nhà ở","code": "NNO","color": "rgb(164, 124, 0)"},{"name": "Đường, quảng trường, nhà ga và bến - bãi đỗ xe Thành phố","code": "DQT","color": "rgb(128, 128, 128)"},{"name": "Đất du lịch, nghỉ dưỡng","code": "DDL","color": "rgb(254, 2, 255)"},{"name": "Đất trồng lúa","code": "LUC","color": "rgb(6, 200, 129)"}
                ]
            }
        },
        methods: {
            open: function(){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            close: function(e) {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        computed: {
            colors_filter: function(){
                let vm = this;
                return vm.colors_sdd.filter((item)=>{
                    return vm.keyword == '' || item.code.toLowerCase().indexOf(vm.keyword.trim().toLowerCase()) > -1;
                })
            }
        }
    });

    Vue.component('login', {
        template: `
            <div class="modal">
                <div class="modal-body animate">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">{{ mode == 'login' ? 'Tài khoản' : 'Quên mật khẩu' }}</div>
                    <div>Nếu bạn chưa có tài khoản vui lòng điền đầy đủ thông tin số điện thoại và mật khẩu sau đó nhấn nút "đăng ký" để tạo tài khoản</div>
                    <div class="login">
                        <div class="d-flex mb-1">
                            <div class="flex-1">
                                <label class="sub-title">Số điện thoại</label>
                                <input type="text" v-model="form.phone" placeholder="Nhập số điện thoại">
                            </div>
                        </div>
                        <template v-if="mode == 'login'">
                            <div class="d-flex mb-1 pb-1">
                                <div class="flex-1">
                                    <label class="sub-title">Mật khẩu</label>
                                    <div class="input-group">
                                        <input type="password" ref="passwordinput" v-model="form.pin" @keyup.enter="login($event)">
                                        <div class="icon" @click.stop.prevent="viewPassword()">
                                            <svg v-if="type == 'password'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M279.6 160.4C282.4 160.1 285.2 160 288 160C341 160 384 202.1 384 256C384 309 341 352 288 352C234.1 352 192 309 192 256C192 253.2 192.1 250.4 192.4 247.6C201.7 252.1 212.5 256 224 256C259.3 256 288 227.3 288 192C288 180.5 284.1 169.7 279.6 160.4zM480.6 112.6C527.4 156 558.7 207.1 573.5 243.7C576.8 251.6 576.8 260.4 573.5 268.3C558.7 304 527.4 355.1 480.6 399.4C433.5 443.2 368.8 480 288 480C207.2 480 142.5 443.2 95.42 399.4C48.62 355.1 17.34 304 2.461 268.3C-.8205 260.4-.8205 251.6 2.461 243.7C17.34 207.1 48.62 156 95.42 112.6C142.5 68.84 207.2 32 288 32C368.8 32 433.5 68.84 480.6 112.6V112.6zM288 112C208.5 112 144 176.5 144 256C144 335.5 208.5 400 288 400C367.5 400 432 335.5 432 256C432 176.5 367.5 112 288 112z"/></svg>
                                            <svg v-if="type != 'password'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M150.7 92.77C195 58.27 251.8 32 320 32C400.8 32 465.5 68.84 512.6 112.6C559.4 156 590.7 207.1 605.5 243.7C608.8 251.6 608.8 260.4 605.5 268.3C592.1 300.6 565.2 346.1 525.6 386.7L630.8 469.1C641.2 477.3 643.1 492.4 634.9 502.8C626.7 513.2 611.6 515.1 601.2 506.9L9.196 42.89C-1.236 34.71-3.065 19.63 5.112 9.196C13.29-1.236 28.37-3.065 38.81 5.112L150.7 92.77zM223.1 149.5L313.4 220.3C317.6 211.8 320 202.2 320 191.1C320 180.5 316.1 169.7 311.6 160.4C314.4 160.1 317.2 159.1 320 159.1C373 159.1 416 202.1 416 255.1C416 269.7 413.1 282.7 407.1 294.5L446.6 324.7C457.7 304.3 464 280.9 464 255.1C464 176.5 399.5 111.1 320 111.1C282.7 111.1 248.6 126.2 223.1 149.5zM320 480C239.2 480 174.5 443.2 127.4 399.4C80.62 355.1 49.34 304 34.46 268.3C31.18 260.4 31.18 251.6 34.46 243.7C44 220.8 60.29 191.2 83.09 161.5L177.4 235.8C176.5 242.4 176 249.1 176 255.1C176 335.5 240.5 400 320 400C338.7 400 356.6 396.4 373 389.9L446.2 447.5C409.9 467.1 367.8 480 320 480H320z"/></svg>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="d-flex mb-1">
                                <label class="checkbox">
                                    <input type="checkbox" v-model="form.save_password" />
                                    <span>Lưu thông tin đăng nhập</span>
                                </label>
                            </div>
                            <div style="mt-1 mb-1">
                                <span class="mr-1">Hỗ trợ:</span>
                                <a class="text-link" @click.stop.prevent="goToFacebook($event)">Facebook</a>
                                <a class="text-link ml-1" @click.stop.prevent="mode = 'reset'">Quên mật khẩu?</a>
                            </div>
                        </template>

                        <div class="d-flex mt-1">
                            <template v-if="mode == 'login'">
                                <button class="btn-primary" @click.stop.prevent="login($event)">{{ sending ? 'Chờ kiểm tra' : 'Đăng nhập' }}</button>
                                <button class="btn-default ml-1" @click.stop.prevent="register($event)">Tạo tài khoản</button>
                            </template>
                            <template v-if="mode == 'reset'">
                                <button class="btn-primary" @click.stop.prevent="sendPassword($event)">{{ sending ? 'Chờ kiểm tra' : 'Xác nhận' }}</button>
                                <button class="btn-default ml-1" @click.stop.prevent="mode = 'login'">Quay lại</button>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                mode: 'login',
                form: {
                    phone: '',
                    pin: '',
                    save_password: true
                },
                callback: null,
                sending: false,
                type: 'password'
            }
        },
        methods: {
            sendPassword: function(event){
                let vm = this;
                if(vm.form.phone == ''){
                    return;
                }
                vm.sending = true;
                vm.$root.postData(vm.$root.setting.api_resource.send_otp, vm.form).then(res => {
                    vm.sending = false;
                    if(!res.error){
                        vm.$root.$refs.verify_password.open({
                            phone: vm.form.phone,
                            callback: function(verified){
                                if(verified){
                                    vm.form.pin = verified.pin;
                                    vm.login(event);
                                    vm.callback = function(){
                                        vm.close();
                                        vm.$root.$refs.changepin.open({
                                            form: {
                                                old_pin: verified.pin,
                                                new_pin: ''
                                            }
                                        });
                                    }
                                }
                            }
                        });
                    }else{
                        vm.$root.showMessageBox(res.message);
                    }
                });
            },
            goToFacebook: function(e){
                let vm = this;
                let url = vm.$root.setting.facebook_url;
                vm.$root.openLink(url);
            },
            viewPassword: function(){
                this.$refs.passwordinput.type = this.$refs.passwordinput.type == 'text' ? 'password' : 'text';
                this.type = this.type == 'password' ? 'text' : 'password';
            },
            register: function(e){
                let vm = this;
                if(vm.form.phone == '' && vm.form.pin == ''){
                    vm.$root.showMessageBox("Vui lòng nhập đầy đủ thông tin trước khi đăng ký tài khoản");
                    return;
                }
                vm.sending = true;
                vm.$root.postData(vm.$root.setting.api_resource.create_account, {
                    phone: vm.form.phone,
                    pin: vm.form.pin,
                    device_id: vm.$root.device_id,
                    device_token: vm.$root.device_token
                }).then(res => {
                    vm.sending = false;
                    if(!res.error){
                        vm.login(e);
                    }else{
                        vm.$root.showMessageBox(res.message);
                    }
                });
            },
            login: function(e){
                let vm = this;
                if(vm.form.phone == '' && vm.form.pin == ''){
                    return;
                }
                vm.sending = true;
                vm.$root.postData(vm.$root.setting.api_resource.login, vm.form).then(res => {
                    vm.sending = false;
                    if(!res.error){
                        vm.$root.u = res.data;
                        vm.close();
                        
                        // x00.x0(x0.xx0('dA=='), vm.$root.x00(res.data));

                        if(vm.form.save_password){
                            x00.x0(x0.xx0('aQ=='), vm.$root.x00(vm.form));
                        }else{
                            x00.x0x(x0.xx0('aQ=='));
                        }

                        if(res.data.is_expired || res.data.point <= 0 || res.data.package_id == 0){
                            let message = "Bạn cần mua thêm gói cước để tiếp tục sử dụng vì gói của bạn đã " + (res.data.is_expired ? 'hết thời hạn sử dụng' : 'hết lượt sử dụng');
                            if(res.data.package_id == 0){
                                message = "Tài khoản của bạn chưa mua gói cước vui lòng thanh toán gói cước để sử dụng dịch vụ";
                            }

                            vm.$root.$refs.confirm.open({
                                title: 'Thông báo',
                                message: message,
                                callback: function(status){
                                    if(status){
                                        vm.$root.$refs.payment.open({
                                            has_reset: false
                                        });
                                    }
                                }
                            });
                        }else{
                            if(typeof vm.callback == 'function'){
                                vm.callback(res.data);
                            }
                        }

                    }else{
                        vm.$root.showMessageBox(res.message);
                    }
                });
            },
            open: function(option){
                this.callback = option && typeof option.callback=='function' ? option.callback : null;
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        mounted: function(){
            let s = x00.x00(x0.xx0('aQ=='));
            if(s){
                this.form = this.$root.xx0x(s);
            }
        }
    });

    Vue.component('payment', {
        template: `
        <div class="modal">
            <div class="modal-body animate">
                <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                <div class="modal-title">Thông tin thanh toán</div>
                <div class="payment">
                    <div class="body">
                        <div class="packages">
                            <template v-for="item in packages">
                                <div class="package-item">
                                    <div class="name">{{ item.name }}</div>
                                    <div>{{ item.description }}</div>
                                </div>
                            </template>
                        </div>
                        <div class="alert alert-success">
                            <div>Vui lòng chuyển khoản (Internet Banking) nội dung chuyển khoản nhập số điện thoại (viết liền không khoảng trắng) hệ thống sẽ tự kích hoạt sđt trong nội dung khi nhận được tiền</div>
                        </div>
                        <div class="payment-account">
                            <template v-for="(item, index) in accounts">
                                <div class="item">
                                    <div class="bank-name">{{ index + 1 }}. {{ item.id }}</div>
                                    <div class="account-name">{{ item.code }} - {{ item.name }}</div>
                                    <div class="branch">{{ item.branch }}</div>
                                    <div class="qr-item" @click.stop.prevent="showQR($event, item)">QR thanh toán</div>
                                </div>
                            </template>
                        </div>
                        <div style="text-align: center;display: flex;justify-content: center;" class="mt-1">
                            <div class="open-messenger" @click.stop.prevent="openSupportLink($event)">
                                <div class="logo-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800"><radialGradient id="a" cx="101.9" cy="809" r="1.1" gradientTransform="matrix(800 0 0 -800 -81386 648000)" gradientUnits="userSpaceOnUse"><stop offset="0" style="stop-color:#09f"/><stop offset=".6" style="stop-color:#a033ff"/><stop offset=".9" style="stop-color:#ff5280"/><stop offset="1" style="stop-color:#ff7061"/></radialGradient><path fill="url(#a)" d="M400 0C174.7 0 0 165.1 0 388c0 116.6 47.8 217.4 125.6 287 6.5 5.8 10.5 14 10.7 22.8l2.2 71.2a32 32 0 0 0 44.9 28.3l79.4-35c6.7-3 14.3-3.5 21.4-1.6 36.5 10 75.3 15.4 115.8 15.4 225.3 0 400-165.1 400-388S625.3 0 400 0z"/><path fill="#FFF" d="m159.8 501.5 117.5-186.4a60 60 0 0 1 86.8-16l93.5 70.1a24 24 0 0 0 28.9-.1l126.2-95.8c16.8-12.8 38.8 7.4 27.6 25.3L522.7 484.9a60 60 0 0 1-86.8 16l-93.5-70.1a24 24 0 0 0-28.9.1l-126.2 95.8c-16.8 12.8-38.8-7.3-27.5-25.2z"/></svg></div>
                                <div class="messenger-content">
                                    <div class="messenger-title">Liên hệ qua Messenger</div>
                                    <div class="messenger-content">Facebook QH Việt</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `,
        data: function(){
            return {
                packages: [
                    {
                        name: '120,000 vnđ',
                        description: '160 lượt / 60 ngày sử dụng'
                    },
                    {
                        name: '350,000 vnđ',
                        description: '360 lượt / 180 ngày sử dụng'
                    },
                    {
                        name: '680,000 vnđ',
                        description: '720 lượt / 365 ngày sử dụng'
                    }
                ],
                accounts: [],
                has_reset: false
            }
        },
        methods: {
            openSupportLink: function(e){
                this.$root.openLink(this.$root.setting.facebook_url);
            },
            showQR: function(e, item){
                let vm = this;
                vm.close();
                let prices = [120000, 350000, 680000];

                vm.$root.$refs.qrbox.open({
                    method: item,
                    prices: prices,
                    default_price: 120000
                })
            },
            loadAccounts: function(){
                let vm = this;
                const response = fetch('https://app.qhviet.com/open-api/listBankAccountV1?app=qhv', {
                    method: 'GET',
                    mode: 'cors',
                    cache: 'no-cache',
                    credentials: 'same-origin',
                    headers: {},
                    redirect: 'follow',
                    referrerPolicy: 'no-referrer'
                })
                .then(res => res.json())
                .then((res)=>{
                    vm.accounts = res.map((e)=>{
                        let item = {};
                        item.id = e.bank_name;
                        item.name = e.account_name;
                        item.code = e.account_number;
                        item.branch = 'Chi nhánh Hồ Chí Minh';
                        return item;
                    });
                })
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
                this.loadAccounts();
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        },
        mounted: function(){
        }
    });

    Vue.component('qrbox', {
        template: `
        <div class="modal modal-center" @click="watchClickOutsite($event)">
            <div class="modal-body animate" ref="modalbody">
                <div class="qrbox">
                    <div class="qrbody">
                        <div class="priceList">
                            <template v-for="(item, index) in prices">
                                <div class="item" :class="item == active_price ? 'active' : ''" @click.stop.prevent="selectPriceItem($event, item)">{{ item | format-price }}</div>
                            </template>
                        </div>
                        <div class="qr">
                            <img v-if="qr_url" :src="qr_url" />
                            <span>Loading...</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        ` ,
        data: function(){
            return {
                active_price: 0,
                prices: [],
                method: null
            }
        },
        filters: {
            'format-price': function(val){
                return (Number(val) / 1000) + 'K';
            }  
        },
        methods: {
            selectPriceItem: function(e, item){
                let vm = this;
                vm.active_price = 0;
                setTimeout(()=>{
                    vm.active_price = item;
                }, 100);
            },
            open: function(option){
                this.method = option.method;
                this.prices = option.prices;
                this.active_price = option.default_price;
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            },
            watchClickOutsite: function(e){
                if (!this.$refs.modalbody.contains(e.target)){
                    this.close();
                }
            },
        },
        computed: {
            qr_url: function(){
                if(this.method && this.$root.u && this.active_price != 0){
                    let bankcode_arr = {
                        'mbbank': '970422',
                        'bidv': '970418',
                        'vietcombank': '970436',
                        'techcombank': '970407',
                        'acb': '970416',
                        'agribank': '970405',
                        'sacombank': '970403',
                        'msb': '970426',
                        'vietinbank': '970415',
                        'vpbank': '970432',
                        'tpbank': '970423',
                        'hdbank': '970437'
                    };

                    let bankId = bankcode_arr[this.method.id.toLowerCase()];

                    return `https://img.vietqr.io/image/${bankId}-${this.method.code}-compact2.png?amount=${this.active_price}&addInfo=${this.$root.u.phone} qhv&accountName=${this.method.name}`;
                }else{
                    return null;
                }
            }
        },
        mounted: function(){

        }
    });

    Vue.component('confirm', {
        template: `
        <div class="modal modal-center">
            <div class="modal-body animate">
                <div class="modal-title">{{ title }}</div>
                <div class="modal-description">{{ message }}</div>
                <div class="d-flex mt-1">
                    <button class="btn btn-primary mr-1 flex-1" @click.stop.prevent="apply($event)">Xác nhận</button>
                    <button class="btn btn-default flex-1" @click.stop.prevent="cancel($event)">Hủy bỏ</button>
                </div>
            </div>
        </div>
        `,
        data: function(){
            return {
                message: '',
                callback: null,
                title: 'Xác nhận thao tác'
            }
        },
        methods: {
            apply: function(e){
                if(typeof this.callback == 'function'){
                    this.callback(true);
                }
                this.close();
            },
            cancel: function(e){
                if(typeof this.callback == 'function'){
                    this.callback(false);
                }
                this.close();
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.$el.classList.add('open');
                this.message = typeof option.message != 'undefined' ? option.message : '';
                this.title = typeof option.title != 'undefined' ? option.title : 'Xác nhận thao tác';
                this.callback = typeof option.callback != 'undefined' ? option.callback : null;
            },
            close: function() {
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            }
        }
    });

    Vue.component('sliderimage', {
        template: `
            <div class="modal full-screen">
                <div class="modal-body animate" ref="modalbody">
                    <div class="slider-current-image">
                        <div class="prev-icon" @click.stop.prevent="prevImage()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M96 480c-8.188 0-16.38-3.125-22.62-9.375c-12.5-12.5-12.5-32.75 0-45.25L242.8 256L73.38 86.63c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0l192 192c12.5 12.5 12.5 32.75 0 45.25l-192 192C112.4 476.9 104.2 480 96 480z"></path></svg></div>
                        <div class="nav">{{ index + 1 }} / {{ images.length }}</div>
                        <div class="next-icon" @click.stop.prevent="nextImage()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M96 480c-8.188 0-16.38-3.125-22.62-9.375c-12.5-12.5-12.5-32.75 0-45.25L242.8 256L73.38 86.63c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0l192 192c12.5 12.5 12.5 32.75 0 45.25l-192 192C112.4 476.9 104.2 480 96 480z"></path></svg></div>
                        <div class="close-icon" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    </div>
                    <div class="slider-box" ref="slider">
                        <div class="slider-container" ref="slides">
                            <div class="slider-item" v-for="item in images">
                                <img :src="item" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                images: [],
                callback: null,
                index: 0
            }
        },
        methods: {
            prevImage: function(){
                if(this.index > 0){
                    this.index = this.index - 1;
                    this.updateSlide();
                }
            },
            nextImage: function(){
                if(this.index < this.images.length - 1){
                    this.index = this.index + 1;
                    this.updateSlide();
                }
            },
            handleTouchStart: function(e){
                window.startX = e.touches[0].clientX;
            },
            handleTouchEnd: function(e){
                let total = this.images.length;
                let endX = e.changedTouches[0].clientX;
                if (window.startX - endX > 50) { // vuốt trái
                    if(this.index < total - 1){
                        this.index = this.index + 1;
                    }
                } else if (endX - window.startX > 50) { // vuốt phải
                    if(this.index > 0){
                        this.index = this.index - 1;
                    }
                }

                this.updateSlide();
            },
            setUpEvent: function(){
                let vm = this;
                window.startX = 0;
                vm.$refs.slider.addEventListener("touchstart", vm.handleTouchStart);
                vm.$refs.slider.addEventListener("touchend", vm.handleTouchEnd);
                vm.updateSlide();
            },
            updateSlide: function(){
                this.$refs.slides.style.opacity = 0;
                setTimeout(()=>{
                    this.$refs.slides.style.transform = `translateX(-${this.index * 100}%)`;
                }, 300);

                setTimeout(()=>{
                    this.$refs.slides.style.opacity = 1;
                }, 400);
            },
            open: function(option){
                const totalOpened = document.querySelectorAll('.modal.open').length;
                this.$el.style.zIndex = 99993 + totalOpened;
                this.callback = option && typeof option.callback == 'function' ? option.callback : null;
                this.images = option && typeof option.images != 'undefined' ? option.images : [];
                this.index = option && typeof option.index != 'undefined' ? option.index : 0;
                this.setUpEvent();
                setTimeout(()=>{
                    this.$el.classList.add('open');
                }, 100);
            },
            cancel: function(){
                if(typeof this.callback == 'function'){
                    this.callback();
                }
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
            },
            close: function() {
                this.$refs.slider.removeEventListener("touchstart", this.handleTouchStart);
                this.$refs.slider.removeEventListener("touchend", this.handleTouchEnd);
                this.$el.classList.remove('open');
                this.$el.style.removeProperty('z-index');
                if(typeof this.callback == 'function'){
                    this.callback();
                }
            }
        }
    });

    Vue.component('verify_password', {
        template: `
            <div class="modal modal-center">
                <div class="modal-body animate">
                    <div class="modal-close-btn" @click.stop.prevent="close()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M310.6 361.4c12.5 12.5 12.5 32.75 0 45.25C304.4 412.9 296.2 416 288 416s-16.38-3.125-22.62-9.375L160 301.3L54.63 406.6C48.38 412.9 40.19 416 32 416S15.63 412.9 9.375 406.6c-12.5-12.5-12.5-32.75 0-45.25l105.4-105.4L9.375 150.6c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L160 210.8l105.4-105.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-105.4 105.4L310.6 361.4z"/></svg></div>
                    <div class="modal-title">Nhập mã xác nhận</div>
                    <div class="mb-1">Một mã xác nhận đã gửi về Zalo (số điện thoại bạn đăng ký), vui lòng nhập mã vào khung bên dưới</div>
                    <div class="otpform mb-1">
                        <input type="text" v-model="otp" inputmode="decimal" />
                    </div>
                    <div class="d-flex">
                        <button class="btn btn-primary mr-1" :disabled="phone.length < 6 || sending" @click.stop.prevent="apply($event)">Xác nhận</button>
                        <button class="btn btn-default mr-1" @click.stop.prevent="cancel($event)">Hủy bỏ</button>
                    </div>
                </div>
            </div>
        `,
        data: function(){
            return {
                sending: false,
                phone: '',
                otp: '',
                callback: null
            }
        },
        methods: {
            apply: function(event){
                let vm = this;
                event.target.classList.add("ontap");
                setTimeout(()=>{
                    event.target.classList.remove("ontap");
                    vm.sending = true;
                    vm.$root.postData(vm.$root.setting.api_resource.check_otp, {
                        phone: vm.phone,
                        otp: vm.otp
                    }).then(res => {
                        vm.sending = false;
                        if(!res.error){
                            vm.close();
                            if(typeof vm.callback == 'function'){
                                vm.callback(res.data);
                            }
                        }else{
                            vm.$root.showMessageBox(res.message);
                        }
                    });
                }, 100);
            },
            cancel: function(){
                if(typeof this.callback == 'function'){
                    this.callback(false);
                }
                this.close();
            },
            open: function(option){
                this.$el.classList.add('open');
                this.phone = typeof option.phone != 'undefined' ? option.phone : '';
                this.otp = '';
                this.callback = typeof option.callback != 'undefined' ? option.callback : null;
            },
            close: function() {
                this.$el.classList.remove('open');
                if(typeof this.callback == 'function'){
                    this.callback(false);
                }
            }
        }
    });

    new Vue({
        el: '#app',
        data: {
            a: 'K3RpdGxlPVdHUyA4NCAobG9uZy9sYXQpICtwcm9qPWxvbmdsYXQgK2VsbHBzPVdHUzg0ICtkYXR1bT1XR1M4NCArdW5pdHM9ZGVncmVlcw==',
            b: "K3Byb2o9dG1lcmMgK2xhdF8wPTAgK2xvbl8wPTEwNS43NSAraz0wLjk5OTkgK3hfMD01MDAwMDAgK3lfMD0wICtlbGxwcz1XR1M4NCArdG93Z3M4ND0tMTkxLjkwNDQxNDI5LC0zOS4zMDMxODI3OSwtMTExLjQ1MDMyODM1LDAuMDA5Mjg4MzYsLTAuMDE5NzU0NzksMC4wMDQyNzM3MiwwLjI1MjkwNjI3OCArdW5pdHM9bSArbm9fZGVmcw==",
            c: '3ee969187bdb54e372edf350aea847e1ba6016ff',
            e: null,
            provinces: [],
            u: null,
            setting: null,
            socket: null,
            app_version: null
        },
        methods: {
            x0: function(o){
                var a = [];
                for (var n = 0, l = o.length; n < l; n ++) {
                    var h = Number(o.charCodeAt(n)).toString(parseInt(x0.xx0('MTY=')));
                    a.push(h);
                }
                return a.join('');
            },
            x00: function(o){
                return this.x0(x0.x0(o));
            },
            xx0: function(){
                let e = this.u.token.split('.');
                let p = parseInt(this.u.phone.substr(this.u.phone.length - 1, 1)) + 1;
                let f = e[1].substr(1, p);
                let s = e[1][0];
                let l = e[1].substr(p+1, e[1].length);
                e[1] = f+s+l;
                return e.join('.');
            },
            xx00: function(o){
                var h  = o.toString();
                var str = '';
                for (var n = 0; n < h.length; n += 2) {
                    str += String.fromCharCode(parseInt(h.substr(n, 2), parseInt(x0.xx0('MTY='))));
                }
                return str;
            },
            xx0x: function(o){
                return x0.x0x(x0.xx0(this.xx00(o)));
            },
            x00x: function(o){
                let i = o[o.length-1][0];
                let pc = this.xx00(o[i][o[i].length - 1]);
                let p = x0.xx0(pc);
                delete o[i][o[i].length - 1];
                let a = [];
                for (let index = 0; index < p.length; index++) {
                    const e = parseInt(p[index]);
                    if(o[e].length > 0){
                        a.push(o[e][0]);
                        delete o[e][0];
                        o[e] = o[e].filter((item)=>{return typeof item!='undefined'});
                    }
                }
                return a.join('');
            },
            openLink: function(url){
                window.open(url, '_blank');
            },
            reloadC: async function(coordinates){
                if(!this.$root.e && typeof proj4!='undefined'){
                    this.$root.e = proj4;
                }

                if(typeof coordinates!='undefined'){
                    this.b = btoa('+proj=tmerc +lat_0=0 +lon_0='+coordinates+' +k=0.9999 +x_0=500000 +y_0=0 +ellps=WGS84 +towgs84=-191.90441429,-39.30318279,-111.45032835,0.00928836,-0.01975479,0.00427372,0.252906278 +units=m +no_defs');
                }
            },
            postData: function(url = '', data = {}, method='POST') {
                let vm = this;
                return new Promise((resolve, reject) => {
                    if(url.indexOf('http://') > -1 || url.indexOf('https://') > -1){
                        var api = url;
                    }else{
                        var api = vm.$root.setting ? vm.$root.setting.api_resource.base + url : url;
                    }

                    var headers = {
                        'Content-Type': 'application/json'
                    };
                    headers[atob('dG9rZW4=')] = vm.u ? vm.xx0() : '';

                    window.WORKERS_ARR.HTTP_WORKER.call({url: api, headers: headers, body: vm.x00(data)}, (res)=>{
                        if(res){
                            res = vm.x00x(res);
                            res = vm.xx0x(res);
                        
                            if(res.hasOwnProperty('error_code')){
                                if(res.error_code == 'TOKEN_INVALID'){
                                    localStorage.removeItem('t');
                                    vm.u = null;
                                    vm.$refs.login.open();
                                    vm.$root.showMessageBox('Phiên đăng nhập của bạn đã hết thời hạn vui lòng đăng nhập lại tài khoản');
                                }
                            }

                            resolve(res);
                        }else{
                            reject('Không thể tải dữ liệu từ máy chủ vui lòng tắt ứng dụng và thử lại sau ít phút');
                        }
                    });
                });
            },
            postFileData: function(url = '', data = {}, method='POST'){
                let vm = this;
                return new Promise((resolve, reject) => {
                    if(url.indexOf('http://') > -1 || url.indexOf('https://') > -1){
                        var api = url;
                    }else{
                        var api = vm.$root.setting ? vm.$root.setting.api_resource.base + url : url;
                    }

                    var headers = {};
                    headers[atob('dG9rZW4=')] = vm.u ? vm.xx0() : '';

                    const formData  = new FormData();
                    for(const name in data) {
                        if(name == 'file'){
                            formData.append(name, data[name], 'ocr.jpg');
                        }else{
                            formData.append(name, typeof data[name] == 'object' ? JSON.stringify(data[name]) : data[name]);
                        }
                    }
                    
                    fetch(api, {
                        method: typeof method!='undefined' ? method : 'GET',
                        mode: 'cors',
                        headers: headers,
                        body: formData
                    })
                    .then(res => res.json())
                    .then((res)=>{
                        res = vm.x00x(res);
                        res = vm.xx0x(res);

                        resolve(res);
                    });
                });
            },
            init: function(){
                let vm = this;
                vm.$root.postData(SETTINGS_URL).then(res => {
                    if(!res.error){
                        vm.setting = res.data;
                        document.getElementById('loadingpage').classList.add('hide');
                        vm.afterInit();
                    }
                });
            },
            afterInit: function(){
                if(window.innerWidth <= 1024){
                    this.$root.$refs['download-app'].open();
                }else{
                    // Chọn mặc định hành chính 2 cấp
                    this.setAppVersion(2);

                    this.$refs['app-map'].createMaps({
                        center: {
                            lat: 10.803630552703, 
                            lng: 106.671237945557
                        }
                    });

                    this.$refs.login.login();   
                }
            },
            setAppVersion: function(versionCode){
                let appVersions = [{code: 2, name: "Hành chính 2 cấp"}, {code: 3, name: "Hành chính 3 cấp"}];
                let find = appVersions.find((e)=> e.code == versionCode);
                if(find){
                    this.app_version = find;
                    setTimeout(()=>{
                        this.$refs['app-map'].parcel.is_show = false;
                        this.$refs['app-map'].$refs['province-box'].$el.classList.remove('hide');
                    }, 100)
                }
            },
            checkPackage: function(){
                if(!this.u){
                    return false;
                }else{
                    return true;
                }
            },
            checkExpired: function(){
                let vm = this;
                return new Promise((resolve, reject)=>{
                    vm.$root.postData(vm.$root.setting.api_resource.is_expired, {}).then(res => {
                        if(res.hasOwnProperty('is_expired')){
                            resolve(res.is_expired);
                        }else{
                            resolve(false)
                        }
                    }).catch((msg)=>{
                        resolve(true);
                    });
                });
            },
            showMessageBox: function(message){
                alert(message);
            },
            showConfirmBox: function(option){
                this.$refs.confirm.open(option);
            },
            getGeometryCoordinates: function(geometry){
                switch (geometry.type) {
                    case "Polygon":
                        return geometry.coordinates[0];
                        break;
                    case "LineString":
                        return geometry.coordinates;
                        break;
                    case "Point":
                        return [geometry.coordinates];
                        break;
                    default:
                        return geometry.coordinates;
                        break;
                }
            },
            getItemGeometry: function(item){
                let geometry = null;
                if(item.hasOwnProperty('geometry') && item.geometry != ''){
                    geometry = typeof item.geometry == 'string' ? JSON.parse(item.geometry) : item.geometry;
                } else if(item.hasOwnProperty('points') && item.points != ''){
                    let points = typeof item.points == 'string' ? JSON.parse(item.points) : item.points;
                    if(points.length == 1){
                        points = points.map(point => [point.lng, point.lat]);
                        geometry = {
                            type: "Point",
                            coordinates: points[0]
                        }
                    } else {
                        geometry = {
                            type: "Polygon",
                            coordinates: [points.map(point => [point.lng, point.lat])]
                        }
                    }
                }

                return geometry;
            },
            getCenterGeometry: function(geometry){
                let feature = L.geoJSON({
                    type: 'Feature',
                    geometry: geometry
                });

                return feature.getBounds().getCenter();
            },
            getGoogleMapURL: function(point){
                if(typeof window.webkit != 'undefined' && typeof window.webkit.messageHandlers!='undefined'){
                    var mapURL = 'https://google.com/maps?q=';
                    return mapURL + point.lat + ',' + point.lng + '&z=19';
                }else{
                    var mapURL = 'https://www.google.com/maps/place/';
                    return mapURL + point.lat + ',' + point.lng;
                }

                return null;
            },
            initSocket: function(){
                let vm = this;
                vm.socket = io("https://app.qhviet.com:8443/qhv", {
                    auth: {
                        href: location.href,
                        app: 'qhv-web',
                        device_id: vm.u.phone,
                        v: 1
                    }
                });
            }
        },
        watch: {
            'u': {
                deep: true,
                handler: function(newval){
                    if(newval){
                        this.initSocket();
                    }
                }
            }
        },
        mounted: function(){
            this.init();
        },
        created: function(){

        }
    })
})()