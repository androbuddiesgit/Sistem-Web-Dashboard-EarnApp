const { createApp, ref, onMounted } = Vue;

createApp({
    setup() {
        const nodes = ref([]);
        const botsData = ref([]);
        const loading = ref(false);
        const showAddNode = ref(false);
        
        const newNode = ref({ ip: '', port: 22, username: 'root', password: '' });
        
        const logModal = ref({ show: false, loading: false, ip: '', container: '', logs: '' });
        
        const deploySuccess = ref(false);
        const deployData = ref({});

        const fetchData = async () => {
            loading.value = true;
            try {
                // Fetch nodes
                const resNodes = await fetch('/api/nodes');
                nodes.value = await resNodes.json();
                
                // Fetch bots
                const resBots = await fetch('/api/bots');
                botsData.value = await resBots.json();
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
                    newNode.value = { ip: '', port: 22, username: 'root', password: '' };
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
                const res = await fetch('/api/bots/deploy', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip })
                });
                const data = await res.json();
                if(res.ok) {
                    deployData.value = data;
                    deploySuccess.value = true;
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

        onMounted(() => {
            fetchData();
        });

        return {
            nodes, botsData, loading, showAddNode, newNode, logModal, deploySuccess, deployData,
            fetchData, addNode, removeNode, botAction, deployBot, viewLogs
        };
    }
}).mount('#app');
