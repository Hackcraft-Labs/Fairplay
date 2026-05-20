import { Routes } from '@angular/router';
import { DashboardComponent } from './features/dashboard/dashboard';
import { DetectionsListComponent } from './features/detections/detections-list';
import { DetectionDetailComponent } from './features/detections/detection-detail';
import { DetectionFormComponent } from './features/detections/detection-form';
import { IocsListComponent } from './features/iocs/iocs-list';
import { IocDetailComponent } from './features/iocs/ioc-detail';
import { IocFormComponent } from './features/iocs/ioc-form';

export const routes: Routes = [
	{ path: '', pathMatch: 'full', component: DashboardComponent },
	{ path: 'detections', component: DetectionsListComponent },
	{ path: 'detections/new', component: DetectionFormComponent },
	{ path: 'detections/:fileHash/edit', component: DetectionFormComponent },
	{ path: 'detections/:fileHash', component: DetectionDetailComponent },
	{ path: 'iocs', component: IocsListComponent },
	{ path: 'iocs/new', component: IocFormComponent },
	{ path: 'iocs/:name/edit', component: IocFormComponent },
	{ path: 'iocs/:name', component: IocDetailComponent },
	{ path: '**', redirectTo: '' }
];
