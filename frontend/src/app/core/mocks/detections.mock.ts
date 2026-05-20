import { Detection } from '../models/detection';

export const MOCK_DETECTIONS: Detection[] = [
    {
        name: 'Trojan.Win32.Agent',
        file_hash: 'b3f2b7db6ff1a7e3f884f94280b808dce1d2d5fda6bb134f4e6b9df41fce21a1',
        sources: ['VirusTotal', 'MalwareBazaar'],
        initial_detection_time: {
            unix: '1718899200',
            text: '2024-06-20 08:00 UTC'
        },
        extra_info: {
            VirusTotal: ['detections: 34/72', 'sandbox: suspicious behavior'],
            Yara: ['rule: trojan_generic_loader', 'matched section: .text']
        },
        deleted: false
    },
    {
        name: 'PUA.Toolbar.Bundle',
        file_hash: '8a1be3a1e78ccfbcd69f57240e5d593ba5f258f95f0e5305d0a63fbf0d503fd7',
        sources: ['CrowdStrike'],
        initial_detection_time: {
            unix: '1719162000',
            text: '2024-06-23 09:00 UTC'
        },
        extra_info: {
            CrowdStrike: ['policy: low severity', 'quarantined: false']
        },
        deleted: true
    },
    {
        name: 'Ransomware.Sample.Locky',
        file_hash: 'f1f8e1232f5f58e71aa7a5a1684f41f3b9d5c326737c7e1536fbf61d9e01a03c',
        sources: ['SentinelOne', 'Defender for Endpoint'],
        initial_detection_time: {
            unix: '1719705600',
            text: '2024-06-29 16:00 UTC'
        },
        extra_info: {
            SentinelOne: ['storyline id: sl-1908', 'kill chain phase: execution'],
            Network: ['outbound to 185.44.77.21:443']
        },
        deleted: false
    }
];
