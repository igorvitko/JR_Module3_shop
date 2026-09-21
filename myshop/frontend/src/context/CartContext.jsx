import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import * as cartApi from "../api/cart";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [cart, setCart] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshCart = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await cartApi.fetchCart();
      setCart(data);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  const value = useMemo(
    () => ({
      cart,
      isLoading,
      itemCount: cart?.total_items ?? 0,
      refreshCart,
    }),
    [cart, isLoading, refreshCart]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart має використовуватись всередині <CartProvider>.");
  }
  return context;
}
