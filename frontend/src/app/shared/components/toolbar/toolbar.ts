import { Component, EventEmitter, Output } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
	selector: 'fp-toolbar',
	standalone: true,
	imports: [MatToolbarModule, MatButtonModule, MatIconModule],
	templateUrl: './toolbar.html',
	styleUrl: './toolbar.scss'
})
export class ToolbarComponent {
	@Output() menuToggle = new EventEmitter<void>();
	@Output() themeToggle = new EventEmitter<void>();

	onToggleMenu(): void {
		this.menuToggle.emit();
	}

	onToggleTheme(): void {
		this.themeToggle.emit();
	}
}