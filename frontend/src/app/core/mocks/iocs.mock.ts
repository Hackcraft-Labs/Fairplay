import { Ioc } from '../models/ioc';

export const MOCK_IOCS: Ioc[] = [
    {
        name: 'suspicious-domain',
        file_hash: '66ba81fe801ceaf4f9e8d6f5af2f5a95f6f7027d8f07ad3d74fc267866a7e5f1',
        poll_time: 30,
        active: true,
        metadata: {
            type: 'domain',
            value: 'malicious-example[.]com',
            confidence: 'high',
            tags: ['c2', 'phishing']
        }
    },
    {
        name: 'beaconing-ip',
        file_hash: 'a9430cc056deeced3255be7eb4f4e677abdc9f076c0f99f7f95b9ad57df11ce2',
        poll_time: 15,
        active: false,
        metadata: {
            type: 'ip',
            value: '45.77.22.110',
            source: 'threat-intel-feed'
        }
    },
    {
        name: 'payload-sha256',
        file_hash: 'dd91e31f61a8d45ea7f72255be0893d42ef41a40b3ec2b8be40e6f530c2fdb1a',
        poll_time: 60,
        active: true,
        metadata: {
            type: 'hash',
            algorithm: 'sha256',
            severity: 'critical'
        }
    }
];
