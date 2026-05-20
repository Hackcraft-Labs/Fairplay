import { Component, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterOutlet, RouterModule } from '@angular/router';
import { BreakpointObserver } from '@angular/cdk/layout';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { map } from 'rxjs';
import { ToolbarComponent } from './shared/components/toolbar/toolbar';
import { ThemeService } from './core/services/theme';
import { OperatorService } from './core/services/operator';
import { DetectionService } from './core/services/detection';
import { IocService } from './core/services/ioc';
import { RefreshService } from './core/services/refresh';
import { Router } from '@angular/router';

@Component({
	selector: 'fp-root',
	standalone: true,
	imports: [
		RouterOutlet,
		RouterModule,
		MatSidenavModule,
		MatToolbarModule,
		MatListModule,
		MatButtonModule,
		MatIconModule,
		ToolbarComponent
	],
	templateUrl: './app.html',
	styleUrl: './app.scss'
})
export class App {
	protected readonly title = signal('fairplay');

	private readonly themeService = inject(ThemeService);
	private readonly breakpointObserver = inject(BreakpointObserver);
	private readonly operatorService = inject(OperatorService);
	private readonly detectionService = inject(DetectionService);
	private readonly iocService = inject(IocService);
	private readonly refreshService = inject(RefreshService);
	private readonly router = inject(Router);

	readonly isMobile = toSignal(
		this.breakpointObserver.observe('(max-width: 960px)').pipe(map(state => state.matches)),
		{ initialValue: false }
	);

	toggleTheme(): void {
		this.themeService.toggle();
	}

	resetDb(): void {
		const confirmed = window.confirm(
			'Reset database? This will delete ALL detections in the DB.\n\nThis cannot be undone.'
		);
		if (!confirmed) return;

		this.operatorService.resetDb().subscribe({
			next: () => {
				// Keep mock mode consistent with the UI.
				this.detectionService.resetMockStore();
				this.iocService.resetMockStore();

				this.refreshService.notifyDataChanged();

				this.router.navigateByUrl('/');
			},
			error: () => {
				window.alert('Reset failed. Check the API is running, then try again.');
			}
		});
	}
}
