const { createApp, ref, onMounted } = Vue;

createApp({
    setup() {
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

        const fetchData = async () => {
            loading.value = true;
            try {
                // Fetch nodes
                const resNodes = await fetch('/api/nodes');
                nodes.value = await resNodes.json();
                
                // Fetch bots
                const resBots = await fetch('/api/bots');
                botsData.value = await resBots.json();
                
                // Calculate Global Stats
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
                
                // Fetch System Monitor Stats asynchronously
                fetch('/api/monitor').then(res => res.json()).then(data => {
                    const statsMap = {};
                    data.forEach(item => {
                        statsMap[item.ip] = item.data;
                    });
                    sysStats.value = statsMap;
                }).catch(e => console.error("Monitor fetch failed", e));
                
            } catch (err) {
                alert('Gagal mengambil data dari server Backend.');
                console.error(err);
            }
            loading.value = false;
        };

        const addNode = async () => {
            try {
                const res = await fetch('/api/nodes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newNode.value)
                });
                if(res.ok) {
                    showAddNode.value = false;
                    newNode.value = { ip: '', port: 22, username: 'root', password: '', name: '' };
                    fetchData();
                } else {
                    const data = await res.json();
                    alert(data.detail || 'Gagal menambahkan Node');
                }
            } catch(e) {
                alert('Gagal menghubungi server');
            }
        };

        const removeNode = async (ip) => {
            if(!confirm(`Hapus node ${ip}?`)) return;
            await fetch(`/api/nodes/${ip}`, { method: 'DELETE' });
            fetchData();
        };

        const renameNode = async (ip, old_name) => {
            const new_name = prompt(`Masukkan nama baru untuk STB ${ip}:`, old_name || '');
            if (new_name === null || new_name === old_name) return;
            
            try {
                const res = await fetch(`/api/nodes/${ip}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: new_name })
                });
                if(res.ok) {
                    fetchData();
                } else {
                    alert('Gagal mengganti nama node');
                }
            } catch(e) {
                alert('Network error');
            }
        };

        const botAction = async (ip, action, container_name) => {
            let msg = `Yakin ingin melakukan action '${action}' pada bot ${container_name}?`;
            if (action === 'rm -f') msg = `BAHAYA: Yakin ingin MENGHAPUS bot ${container_name}? Anda harus mendaftarkan ulang UUID jika ingin memakainya lagi.`;
            
            if(!confirm(msg)) return;

            loading.value = true;
            try {
                const res = await fetch('/api/bots/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip, action, container_name })
                });
                if (!res.ok) {
                    const err = await res.json();
                    alert(err.detail);
                }
            } finally {
                fetchData();
            }
        };

        const deployBot = async (ip) => {
            if(!confirm(`Deploy (Tanam) 1 Bot Baru secara otomatis ke STB ${ip}?\n\nProses ini memakan waktu beberapa detik untuk memutar UUID dan menghubungi server pusat.`)) return;
            
            loading.value = true;
            try {
                const res = await fetch('/api/deploy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip: ip, count: 1 })
                });
                const data = await res.json();
                if(res.ok && data.results && data.results.length > 0) {
                    if (data.results[0].status === 'success') {
                        deployData.value = data.results[0];
                        deploySuccess.value = true;
                    } else {
                        alert('Gagal Deploy: ' + data.results[0].error);
                    }
                } else {
                    alert('Gagal Deploy: ' + (data.detail || 'Unknown error'));
                }
            } catch(e) {
                alert('Terjadi kesalahan jaringan saat deploy.');
            } finally {
                fetchData();
            }
        };

        const showBulkDeploy = ref(false);
        const bulkDeployForm = ref({ ip: '', count: 1, proxies: '', spoof_hw: false });
        
        const openBulkDeploy = (ip) => {
            bulkDeployForm.value = { ip, count: 5, proxies: '', spoof_hw: false };
            showBulkDeploy.value = true;
        };

        const submitBulkDeploy = async () => {
            if(!confirm(`Yakin ingin menanam ${bulkDeployForm.value.count} bot sekaligus ke STB ${bulkDeployForm.value.ip}?`)) return;
            showBulkDeploy.value = false;
            loading.value = true;
            try {
                const res = await fetch('/api/deploy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bulkDeployForm.value)
                });
                const data = await res.json();
                if(res.ok) {
                    let successCount = data.results.filter(r => r.status==='success').length;
                    let failCount = data.results.filter(r => r.status==='failed').length;
                    alert(`Bulk Deploy Selesai!\n\nBerhasil: ${successCount}\nGagal: ${failCount}\n\nSilakan cek log masing-masing bot untuk detailnya.`);
                } else {
                    alert('Gagal Deploy: ' + (data.detail || 'Unknown error'));
                }
            } catch(e) {
                alert('Terjadi kesalahan jaringan saat deploy.');
            } finally {
                fetchData();
            }
        };

        const viewLogs = async (ip, container_name) => {
            logModal.value = { show: true, loading: true, ip, container: container_name, logs: '' };
            try {
                const res = await fetch(`/api/bots/logs?ip=${ip}&container_name=${container_name}`);
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
                                const res = await fetch(`/api/bots/ip?ip=${ip}&container_name=${container_name}`);
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

        const restartAllBots = async (ip) => {
            if(!confirm(`Restart SEMUA bot di STB ${ip}?`)) return;
            loading.value = true;
            try {
                const res = await fetch('/api/bots/restart_all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip })
                });
                if (!res.ok) alert((await res.json()).detail || 'Failed to restart all');
            } catch(e) {
                alert('Network error');
            } finally {
                fetchData();
            }
        };

        const renameBot = async (ip, old_name) => {
            const new_name = prompt(`Masukkan nama baru untuk bot ${old_name}:\n(Hanya huruf, angka, garis bawah, dan strip)`, old_name);
            if (!new_name || new_name === old_name) return;
            
            if (!/^[a-zA-Z0-9_-]+$/.test(new_name)) {
                alert('Format nama tidak valid! Hanya huruf, angka, _, dan - yang diperbolehkan.');
                return;
            }

            loading.value = true;
            try {
                const res = await fetch('/api/bots/rename', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip, old_name, new_name })
                });
                if (!res.ok) alert((await res.json()).detail || 'Failed to rename');
            } catch(e) {
                alert('Network error');
            } finally {
                fetchData();
            }
        };

        onMounted(() => {
            if (!localStorage.getItem('ea_cluster_welcomed')) {
                showWelcome.value = true;
            }
            fetchData();
        });

        return {
            nodes, botsData, loading, showAddNode, newNode, logModal, deploySuccess, deployData,
            globalStats, sysStats, showBulkDeploy, bulkDeployForm, openBulkDeploy, submitBulkDeploy,
            showWelcome, closeWelcome, openRef,
            fetchData, addNode, removeNode, renameNode, botAction, deployBot, viewLogs, checkIP, restartAllBots, renameBot
        };
    }
}).mount('#app');
