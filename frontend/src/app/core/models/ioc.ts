export interface IocMetadata {
    [key: string]: unknown;
}
  
export interface Ioc {
    name: string;
    file_hash: string;
    poll_time: number;
    metadata?: IocMetadata;
    active?: boolean;
}