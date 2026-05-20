export interface DetectionInitialTime {
    unix: string;
    text: string;
}
  
export interface DetectionExtraInfo {
    [collectorName: string]: string[];
}
  
export interface Detection {
    name: string;
    file_hash: string;
    sources: string[];
    initial_detection_time: DetectionInitialTime;
    extra_info: DetectionExtraInfo;
    deleted?: boolean;
}