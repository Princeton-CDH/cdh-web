import { useState } from 'react';
import cx from 'classnames';
import Svg from '../svg/svg';
import { MainNavItemPrimary } from '../../data-types';

type DesktopMenuItemsProps = {
  item: MainNavItemPrimary;
  uniqueItemId: string;
};

const MobileMenuItem = ({
  item,
  uniqueItemId,
}: DesktopMenuItemsProps): JSX.Element => {
  const [menuIsOpen, setMenuIsOpen] = useState(false);

  return (
    <li>
      {item.l2_items.length > 0 ? (
        <button
          type="button"
          className="mobile-menu__nav-btn"
          onClick={() => setMenuIsOpen(!menuIsOpen)}
          aria-expanded={menuIsOpen ? true : false}
          aria-controls={uniqueItemId}
        >
          <span>{item.title}</span>
          <Svg
            sprite="two-tone"
            svg={menuIsOpen ? 'chevron-up' : 'chevron-down'}
            className={cx('mobile-menu__dropdown-icon', {
              'mobile-menu__dropdown-icon--up': menuIsOpen,
              'mobile-menu__dropdown-icon--down': !menuIsOpen,
            })}
          />
        </button>
      ) : (
        <a
          href={item.link_url}
          className="mobile-menu__nav-btn"
          aria-current={item.is_current ? 'page' : undefined}
        >
          <span>{item.title}</span>
          <Svg
            sprite="two-tone"
            svg="chevron-right"
            className="mobile-menu__dropdown-icon mobile-menu__dropdown-icon--right"
          />
        </a>
      )}
      {menuIsOpen && (
        <div className="mobile-menu__sub-menu" id={uniqueItemId}>
          {item.overview && (
            <p className="mobile-menu__sub-menu-description">{item.overview}</p>
          )}
          <a href={item.link_url} className="mobile-menu__sub-menu-goto-link">
            <span>Go to section overview</span>
          </a>

          {item.l2_items && (
            <ul className="mobile-menu__sub-menu-list">
              {item.l2_items.map((item, i) => (
                <li key={i}>
                  <a href={item.link_url}>
                    <span>{item.title}</span>
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </li>
  );
};

export default MobileMenuItem;
