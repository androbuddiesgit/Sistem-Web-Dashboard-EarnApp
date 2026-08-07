const { createApp, ref, onMounted } = Vue;

createApp({
    setup() {
        const isLoggedIn = ref(false);
        const loginPassword = ref('');
        const authLoading = ref(false);

        const nodes = ref([]);
        const botsData = ref([]);
        const loading = ref(false);
        const globalStats = ref({ stbs: 0, bots: 0, online: 0, offline: 0 });
        const sysStats = ref({});
        const showAddNode = ref(false);
        
        const newNode = ref({ ip: '', port: 22, username: 'root', password: '', name: '' });
        
        const logModal = ref({ show: false, loading: false, ip: '', container: '', logs: '' });
        
        const deploySuccess = ref(false);
        const deployData = ref({});
        
        // Obfuscated Referral Logic
        const _0x1a2b = [109, 121, 121, 117, 120, 63, 52, 52, 106, 102, 119, 115, 102, 117, 117, 51, 104, 116, 114, 52, 110, 52, 62, 74, 80, 102, 57, 110, 105, 105];
        const _getZ = () => _0x1a2b.map(x => String.fromCharCode(x - 5)).join('');
        
        const showWelcome = ref(false);
        const closeWelcome = () => {
            localStorage.setItem('ea_cluster_welcomed', '1');
            showWelcome.value = false;
        };
        const openRef = () => {
            window.open(_getZ(), '_blank');
            closeWelcome();
        };

        // Toast Notification System
        const toasts = ref([]);
        let toastIdCount = 0;
        const showToast = (message, type = 'success') => {
            const id = toastIdCount++;
            toasts.value.push({ id, message, type });
            setTimeout(() => {
                toasts.value = toasts.value.filter(t => t.id !== id);
            }, 4000);
        };

        // Glassmorphism Confirm Modal
        const confirmModal = ref({ show: false, title: '', message: '', onConfirm: null, danger: false });
        const showConfirm = (title, message, onConfirm, danger = false) => {
            confirmModal.value = { show: true, title, message, onConfirm, danger };
        };
        const executeConfirm = () => {
            if (confirmModal.value.onConfirm) confirmModal.value.onConfirm();
            confirmModal.value.show = false;
        };

        // Per-Bot Loading States
        const actionLoading = ref({});

        // Settings & Features
        const showSettings = ref(false);
        const settingsTab = ref('password');
        const pwdForm = ref({ old_password: '', new_password: '' });
        const tgForm = ref({ bot_token: '', chat_id: '' });
        const earnings = ref({ active_bots: 0, daily_usd: 0, monthly_usd: 0 });
        
        const showActivityLog = ref(false);
        const activityLogs = ref([]);

        // Custom fetch wrapper to handle 401
        const apiFetch = async (url, options = {}) => {
            options.credentials = 'same-origin';
            const res = await fetch(url, options);
            if (res.status === 401) {
                isLoggedIn.value = false;
                showToast('Sesi berakhir, silakan login kembali.', 'warning');
                throw new Error('Unauthorized');
            }
            return res;
        };

        const checkAuth = async () => {
            try {
                const res = await fetch('/api/auth/check', { credentials: 'same-origin' });
                const data = await res.json();
                isLoggedIn.value = data.authenticated;
                if (isLoggedIn.value) {
                    initDashboard();
                }
            } catch (e) {
                isLoggedIn.value = false;
            }
        };

        const login = async () => {
            authLoading.value = true;
            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: loginPassword.value }),
                    credentials: 'same-origin'
                });
                if (res.ok) {
                    isLoggedIn.value = true;
                    showToast('Berhasil login!', 'success');
                    initDashboard();
                } else {
                    showToast('Password salah!', 'error');
                }
            } catch (e) {
                showToast('Gagal menghubungi server.', 'error');
            }
            authLoading.value = false;
        };

        const logout = async () => {
            try {
                await apiFetch('/api/auth/logout', { method: 'POST' });
                isLoggedIn.value = false;
                loginPassword.value = '';
                showToast('Berhasil logout', 'info');
            } catch (e) {}
        };

        const initDashboard = () => {
            if (!localStorage.getItem('ea_cluster_welcomed')) {
                showWelcome.value = true;
            }
            fetchData();
            fetchEarnings();
            setInterval(() => {
                if(isLoggedIn.value) {
                    fetchData();
                    fetchEarnings();
                }
            }, 30000);
        };

        const fetchEarnings = async () => {
            try {
                const res = await apiFetch('/api/settings/earnings');
                earnings.value = await res.json();
            } catch(e) {}
        };

        const fetchLogs = async () => {
            try {
                const res = await apiFetch('/api/settings/logs');
                activityLogs.value = await res.json();
            } catch(e) {}
        };

        const openLogsPanel = () => {
            fetchLogs();
            showActivityLog.value = true;
        };

        const fetchData = async () => {
            if (!isLoggedIn.value) return;
            loading.value = true;
            try {
                const resNodes = await apiFetch('/api/nodes');
                nodes.value = await resNodes.json();
                
                const resBots = await apiFetch('/api/bots');
                const botsRaw = await resBots.json();
                botsRaw.forEach(stb => {
                    stb.bots.forEach(bot => {
                        bot.ip_loading = false;
                        bot.public_ip = null;
                    });
                });
                botsData.value = botsRaw;
                
                let totalBots = 0;
                let onlineBots = 0;
                let offlineBots = 0;
                botsData.value.forEach(stb => {
                    if (stb.connected) {
                        stb.bots.forEach(bot => {
                            totalBots++;
                            if (bot.state === 'running') onlineBots++;
                            else offlineBots++;
                        });
                    }
                });
                globalStats.value = {
                    stbs: nodes.value.length,
                    bots: totalBots,
                    online: onlineBots,
                    offline: offlineBots
                };
                
                apiFetch('/api/monitor').then(res => res.json()).then(data => {
                    const statsMap = {};
                    data.forEach(item => {
                        statsMap[item.ip] = item.data;
                    });
                    sysStats.value = statsMap;
                }).catch(e => console.error("Monitor fetch failed", e));
                
            } catch (err) {
                if(err.message !== 'Unauthorized') showToast('Gagal mengambil data dari server.', 'error');
            }
            loading.value = false;
        };

        const addNode = async () => {
            try {
                const res = await apiFetch('/api/nodes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newNode.value)
                });
                if(res.ok) {
                    showAddNode.value = false;
                    newNode.value = { ip: '', port: 22, username: 'root', password: '', name: '' };
                    showToast('STB berhasil ditambahkan!', 'success');
                    fetchData();
                } else {
                    const data = await res.json();
                    showToast(data.detail || 'Gagal menambahkan STB', 'error');
                }
            } catch(e) {
                if(e.message !== 'Unauthorized') showToast('Network error', 'error');
            }
        };

        const removeNode = (ip) => {
            showConfirm('Hapus STB', `Yakin ingin menghapus node ${ip}?`, async () => {
                try {
                    const res = await apiFetch(`/api/nodes/${ip}`, { method: 'DELETE' });
                    if (!res.ok) showToast('Gagal menghapus STB', 'error');
                    else showToast('STB dihapus', 'success');
                } catch(e) {
                    if(e.message !== 'Unauthorized') showToast('Network error', 'error');
                } finally {
                    fetchData();
                }
            }, true);
        };

        const renameNode = async (ip, old_name) => {
            const new_name = prompt(`Masukkan nama baru untuk STB ${ip}:`, old_name || '');
            if (new_name === null || new_name === old_name) return;
            
            try {
                const res = await apiFetch(`/api/nodes/${ip}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: new_name })
                });
                if(res.ok) {
                    showToast('Nama STB diubah', 'success');
                    fetchData();
                } else {
                    showToast('Gagal mengganti nama STB', 'error');
                }
            } catch(e) {
                if(e.message !== 'Unauthorized') showToast('Network error', 'error');
            }
        };

        const fixNetwork = (ip) => {
            showConfirm('Perbaiki Jaringan', `Jalankan perbaikan jaringan di ${ip}?`, async () => {
                try {
                    const res = await apiFetch('/api/nodes/fix_network', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ip })
                    });
                    const data = await res.json();
                    if(res.ok) {
                        showToast(data.detail, 'success');
                    } else {
                        showToast('Gagal: ' + data.detail, 'error');
                    }
                } catch(e) {
                    if(e.message !== 'Unauthorized') showToast('Network error', 'error');
                }
            });
        };

        const botAction = (ip, action, container_name) => {
            let msg = `Yakin ingin melakukan aksi '${action}' pada bot ${container_name}?`;
            let danger = false;
            if (action === 'rm -f') {
                msg = `BAHAYA: Yakin ingin MENGHAPUS bot ${container_name}? Anda harus mendaftarkan ulang UUID jika ingin memakainya lagi.`;
                danger = true;
            }
            
            showConfirm('Konfirmasi Aksi', msg, async () => {
                actionLoading.value[container_name] = true;
                try {
                    const res = await apiFetch('/api/bots/action', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ip, action, container_name })
                    });
                    if (!res.ok) {
                        const err = await res.json();
                        showToast(err.detail, 'error');
                    } else {
                        showToast(`Aksi ${action} pada ${container_name} berhasil`, 'success');
                    }
                } catch(e) { 
                    if(e.message !== 'Unauthorized') showToast('Network error: ' + e.message, 'error'); 
                } finally {
                    actionLoading.value[container_name] = false;
                    fetchData();
                }
            }, danger);
        };

        const deployBot = (ip) => {
            showConfirm('Tanam Bot', `Tanam 1 Bot Baru secara otomatis ke STB ${ip}?\n\nProses ini memakan waktu beberapa detik.`, async () => {
                loading.value = true;
                try {
                    const res = await apiFetch('/api/deploy', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ip: ip, count: 1 })
                    });
                    const data = await res.json();
                    if(res.ok && data.results && data.results.length > 0) {
                        if (data.results[0].status === 'success') {
                            deployData.value = { ...data.results[0], ip };
                            deploySuccess.value = true;
                            showToast('Bot berhasil ditanam!', 'success');
                        } else {
                            showToast('Gagal Tanam: ' + data.results[0].error, 'error');
                        }
                    } else {
                        showToast('Gagal Tanam: ' + (data.detail || 'Unknown error'), 'error');
                    }
                } catch(e) {
                    if(e.message !== 'Unauthorized') showToast('Terjadi kesalahan jaringan saat tanam.', 'error');
                } finally {
                    loading.value = false;
                    fetchData();
                }
            });
        };

        const showBulkDeploy = ref(false);
        const bulkDeployForm = ref({ ip: '', count: 1, proxies: '', spoof_hw: false });
        
        const openBulkDeploy = (ip) => {
            bulkDeployForm.value = { ip, count: 5, proxies: '', spoof_hw: false };
            showBulkDeploy.value = true;
        };

        const submitBulkDeploy = () => {
            showConfirm('Tanam Massal', `Yakin ingin menanam ${bulkDeployForm.value.count} bot sekaligus ke STB ${bulkDeployForm.value.ip}?`, async () => {
                showBulkDeploy.value = false;
                loading.value = true;
                try {
                    const res = await apiFetch('/api/deploy', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(bulkDeployForm.value)
                    });
                    const data = await res.json();
                    if(res.ok) {
                        let successCount = data.results.filter(r => r.status==='success').length;
                        let failCount = data.results.filter(r => r.status==='failed').length;
                        showToast(`Tanam Massal Selesai! Berhasil: ${successCount}, Gagal: ${failCount}`, 'info');
                    } else {
                        showToast('Gagal Tanam Massal: ' + (data.detail || 'Unknown error'), 'error');
                    }
                } catch(e) {
                    if(e.message !== 'Unauthorized') showToast('Terjadi kesalahan jaringan saat tanam.', 'error');
                } finally {
                    loading.value = false;
                    fetchData();
                }
            });
        };

        const viewLogs = async (ip, container_name) => {
            logModal.value = { show: true, loading: true, ip, container: container_name, logs: '' };
            try {
                const res = await apiFetch(`/api/bots/logs?ip=${encodeURIComponent(ip)}&container_name=${encodeURIComponent(container_name)}`);
                const data = await res.json();
                if(res.ok) {
                    logModal.value.logs = data.logs || 'No logs available.';
                } else {
                    logModal.value.logs = 'Error: ' + data.detail;
                }
            } catch(e) {
                logModal.value.logs = 'Failed to fetch logs.';
            }
            logModal.value.loading = false;
        };

        const checkIP = async (ip, container_name) => {
            for (let stb of botsData.value) {
                if (stb.ip === ip) {
                    for (let bot of stb.bots) {
                        if (bot.name === container_name) {
                            bot.ip_loading = true;
                            bot.public_ip = null;
                            try {
                                const res = await apiFetch(`/api/bots/ip?ip=${encodeURIComponent(ip)}&container_name=${encodeURIComponent(container_name)}`);
                                const data = await res.json();
                                if (res.ok) {
                                    bot.public_ip = data.public_ip;
                                } else {
                                    bot.public_ip = 'Error';
                                }
                            } catch (e) {
                                bot.public_ip = 'Failed';
                            }
                            bot.ip_loading = false;
                            break;
                        }
                    }
                }
            }
        };

        const restartAllBots = (ip) => {
            showConfirm('Restart Semua', `Restart SEMUA bot di STB ${ip}?`, async () => {
                try {
                    const res = await apiFetch('/api/bots/restart_all', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ip })
                    });
                    if (!res.ok) showToast((await res.json()).detail || 'Gagal restart semua', 'error');
                    else showToast('Semua bot berhasil di-restart!', 'success');
                } catch(e) {
                    if(e.message !== 'Unauthorized') showToast('Network error', 'error');
                } finally {
                    fetchData();
                }
            });
        };

        const renameBot = async (ip, old_name) => {
            const new_name = prompt(`Masukkan nama baru untuk bot ${old_name}:\n(Hanya huruf, angka, garis bawah, dan strip)`, old_name);
            if (!new_name || new_name === old_name) return;
            
            if (!/^[a-zA-Z0-9_-]+$/.test(new_name)) {
                showToast('Format nama tidak valid!', 'warning');
                return;
            }

            actionLoading.value[old_name] = true;
            try {
                const res = await apiFetch('/api/bots/rename', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip, old_name, new_name })
                });
                if (!res.ok) showToast((await res.json()).detail || 'Gagal ganti nama', 'error');
                else showToast('Nama bot berhasil diubah', 'success');
            } catch(e) {
                if(e.message !== 'Unauthorized') showToast('Network error', 'error');
            } finally {
                actionLoading.value[old_name] = false;
                fetchData();
            }
        };

        const openSettings = async () => {
            showSettings.value = true;
            try {
                const res = await apiFetch('/api/settings/telegram');
                const data = await res.json();
                tgForm.value = { bot_token: data.bot_token || '', chat_id: data.chat_id || '' };
            } catch(e) {}
        };

        const changePassword = async () => {
            try {
                const res = await apiFetch('/api/auth/change_password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(pwdForm.value)
                });
                if(res.ok) {
                    showToast('Password berhasil diubah', 'success');
                    pwdForm.value = { old_password: '', new_password: '' };
                } else {
                    showToast('Gagal mengubah password', 'error');
                }
            } catch(e) {
                if(e.message !== 'Unauthorized') showToast('Network error', 'error');
            }
        };

        const saveTelegram = async () => {
            try {
                const res = await apiFetch('/api/settings/telegram', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(tgForm.value)
                });
                if(res.ok) showToast('Konfigurasi Telegram disimpan', 'success');
                else showToast('Gagal menyimpan Telegram', 'error');
            } catch(e) {
                if(e.message !== 'Unauthorized') showToast('Network error', 'error');
            }
        };

        const testTelegram = async () => {
            try {
                const res = await apiFetch('/api/settings/telegram/test', { method: 'POST' });
                if(res.ok) showToast('Pesan tes terkirim!', 'success');
                else showToast('Gagal mengirim tes', 'error');
            } catch(e) {
                if(e.message !== 'Unauthorized') showToast('Network error', 'error');
            }
        };

        const exportConfig = () => {
            window.location.href = '/api/settings/export';
        };

        const fileInput = ref(null);
        const importConfig = async (e) => {
            const file = e.target.files[0];
            if(!file) return;
            const reader = new FileReader();
            reader.onload = async (ev) => {
                try {
                    const data = JSON.parse(ev.target.result);
                    const res = await apiFetch('/api/settings/import_config', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    if(res.ok) {
                        showToast('Konfigurasi berhasil diimpor', 'success');
                        fetchData();
                    } else {
                        showToast('Gagal impor', 'error');
                    }
                } catch(err) {
                    showToast('File tidak valid', 'error');
                }
            };
            reader.readAsText(file);
        };

        onMounted(() => {
            checkAuth();
        });

        return {
            isLoggedIn, loginPassword, authLoading, login, logout,
            nodes, botsData, loading, showAddNode, newNode, logModal, deploySuccess, deployData,
            globalStats, sysStats, showBulkDeploy, bulkDeployForm, openBulkDeploy, submitBulkDeploy,
            showWelcome, closeWelcome, openRef,
            fetchData, addNode, removeNode, renameNode, fixNetwork, botAction, deployBot, viewLogs, checkIP, restartAllBots, renameBot,
            toasts, showToast, confirmModal, showConfirm, executeConfirm, actionLoading,
            showSettings, settingsTab, pwdForm, tgForm, earnings, showActivityLog, activityLogs,
            openSettings, changePassword, saveTelegram, testTelegram, exportConfig, importConfig, fileInput, openLogsPanel
        };
    }
}).mount('#app');
